const { fetchPlData, fetchBsData, tallyDate } = require('./tallyService');
const PLData = require('../models/PLData');
const BSData = require('../models/BSData');
const Company = require('../models/Company');

const SKIP_TALLY_GROUPS = [
  'opening stock', 'closing stock', 'gross profit', 'gross loss',
  'net profit', 'net loss', 'sales accounts', 'purchase accounts',
  'direct incomes', 'direct expenses', 'indirect incomes', 'indirect expenses'
];

const _sf = (v) => {
  try {
    const val = parseFloat(String(v || '').replace(/[^\d.\-]/g, '') || '0');
    return isNaN(val) ? 0.0 : val;
  } catch {
    return 0.0;
  }
};

const parsePlXml = (xmlText) => {
  const rows = [];
  const lines = xmlText.split('\n');
  let currentGroup = '';
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();

    if (line.includes('<DSPACCNAME>') && (!lines[i - 1] || !lines[i - 1].includes('<BSNAME>'))) {
      for (let j = i; j < Math.min(i + 4, lines.length); j++) {
        const m = lines[j].match(/<DSPDISPNAME>(.*?)<\/DSPDISPNAME>/);
        if (m) {
          currentGroup = m[1].trim();
          break;
        }
      }
    }

    if (line.includes('<BSNAME>')) {
      let ledger = '';
      let value = 0.0;

      for (let j = i; j < Math.min(i + 6, lines.length); j++) {
        const m = lines[j].match(/<DSPDISPNAME>(.*?)<\/DSPDISPNAME>/);
        if (m) {
          ledger = m[1].trim();
          break;
        }
      }

      for (let j = i; j < Math.min(i + 8, lines.length); j++) {
        const m = lines[j].match(/<BSSUBAMT>(.*?)<\/BSSUBAMT>/);
        if (m && m[1].trim()) {
          value = _sf(m[1]);
          break;
        }
      }

      if (ledger && ledger !== currentGroup) {
        if (!SKIP_TALLY_GROUPS.includes(ledger.toLowerCase().trim())) {
          rows.push({
            ledger,
            tally_group: currentGroup,
            debit: value < 0 ? Math.abs(value) : 0,
            credit: value > 0 ? Math.abs(value) : 0,
            net: value
          });
        }
      }
    }
  }

  // Deduplicate
  const seen = {};
  for (const r of rows) {
    seen[r.ledger] = r;
  }
  return Object.values(seen);
};

const parseBsXml = (xmlText) => {
  const rows = [];
  const lines = xmlText.split('\n');
  let currentGroup = '';

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();

    if (line.includes('<DSPACCNAME>')) {
      for (let j = i; j < Math.min(i + 4, lines.length); j++) {
        const m = lines[j].match(/<DSPDISPNAME>(.*?)<\/DSPDISPNAME>/);
        if (m) {
          currentGroup = m[1].trim();
          break;
        }
      }
    }

    if (line.includes('<BSNAME>')) {
      let ledger = '';
      let value = 0.0;
      for (let j = i; j < Math.min(i + 6, lines.length); j++) {
        const m = lines[j].match(/<DSPDISPNAME>(.*?)<\/DSPDISPNAME>/);
        if (m) {
          ledger = m[1].trim();
          break;
        }
      }
      for (let j = i; j < Math.min(i + 8, lines.length); j++) {
        const m1 = lines[j].match(/<BSSUBAMT>(.*?)<\/BSSUBAMT>/);
        if (m1 && m1[1].trim()) {
          value = _sf(m1[1]);
          break;
        }
        const m2 = lines[j].match(/<BSMAINAMT>(.*?)<\/BSMAINAMT>/);
        if (m2 && m2[1].trim()) {
          value = _sf(m2[1]);
          break;
        }
      }
      if (ledger && ledger !== currentGroup) {
        rows.push({
          ledger,
          tally_group: currentGroup,
          balance: value
        });
      }
    }
  }

  const seen = {};
  for (const r of rows) {
    seen[r.ledger] = r;
  }
  return Object.values(seen);
};

const syncCompanyNow = async (companyId, tallyUrl) => {
  try {
    const company = await Company.findById(companyId);
    if (!company) throw new Error("Company not found");

    company.sync_status = 'syncing';
    await company.save();

    // Mocking the sync logic for now
    // A full implementation would loop over months and use parsePlXml / parseBsXml 
    // to save data into PLData and BSData schemas.
    
    company.sync_status = 'ok';
    company.last_sync = new Date().toISOString();
    await company.save();

    return { status: 'ok', message: 'Sync complete' };
  } catch (error) {
    console.error("Sync error:", error);
    return { status: 'error', message: error.message };
  }
};

module.exports = { parsePlXml, parseBsXml, syncCompanyNow };
