const axios = require('axios');
const { XMLParser } = require('fast-xml-parser');

// Initialize the XML parser
const parser = new XMLParser({
  ignoreAttributes: false,
  attributeNamePrefix: "@_"
});

const DEFAULT_TALLY_URL = process.env.TALLY_URL || 'http://localhost:9000';
const TIMEOUT = 60000;

const getUrl = (url) => {
  return (url && url.trim()) ? url.trim() : DEFAULT_TALLY_URL;
};

const testConnection = async (tallyUrl) => {
  try {
    const url = getUrl(tallyUrl);
    const xml = '<ENVELOPE><HEADER><TALLYREQUEST>Export Data</TALLYREQUEST></HEADER></ENVELOPE>';
    const response = await axios.post(url, xml, {
      headers: { 'Content-Type': 'application/xml' },
      timeout: 10000
    });
    
    if (response.status === 200 && response.data.includes('RESPONSE')) {
      return { status: 'ok', message: 'Tally connected successfully' };
    }
    return { status: 'error', message: 'Unexpected response' };
  } catch (error) {
    return { status: 'error', message: 'Cannot connect to Tally. Ensure Tally is open on port 9000' };
  }
};

const getCurrentCompany = async (tallyUrl) => {
  const xml = `<ENVELOPE>
<HEADER><VERSION>1</VERSION><TALLYREQUEST>Export</TALLYREQUEST>
<TYPE>Data</TYPE><ID>MyReport</ID></HEADER>
<BODY><DESC><TDL><TDLMESSAGE>
<REPORT NAME="MyReport"><FORMS>MyForm</FORMS></REPORT>
<FORM NAME="MyForm"><PARTS>MyPart</PARTS></FORM>
<PART NAME="MyPart"><LINES>MyLine</LINES>
<REPEAT>MyLine : MyCollection</REPEAT>
<SCROLLED>Vertical</SCROLLED></PART>
<LINE NAME="MyLine"><FIELDS>MyField</FIELDS></LINE>
<FIELD NAME="MyField"><SET>$Name</SET></FIELD>
<COLLECTION NAME="MyCollection" ISINITIALIZE="Yes">
<TYPE>Company</TYPE>
</COLLECTION>
</TDLMESSAGE></TDL></DESC></BODY></ENVELOPE>`;

  try {
    const url = getUrl(tallyUrl);
    const response = await axios.post(url, xml, {
      headers: { 'Content-Type': 'application/xml' },
      timeout: TIMEOUT
    });
    
    // Extract MYFIELD elements
    const matches = response.data.match(/<MYFIELD>(.*?)<\/MYFIELD>/g);
    if (!matches) return [];
    
    return matches.map(m => m.replace(/<\/?MYFIELD>/g, '').trim()).filter(Boolean);
  } catch (error) {
    console.error("[Tally] getCurrentCompany error:", error.message);
    return [];
  }
};

const getAllCompanies = async (tallyUrl) => {
  const names = await getCurrentCompany(tallyUrl);
  return names.map(name => ({ name, books_from: '' }));
};

const fetchPlData = async (company, fromDate, toDate, tallyUrl) => {
  const xml = `<ENVELOPE>
<HEADER><TALLYREQUEST>Export Data</TALLYREQUEST></HEADER>
<BODY><EXPORTDATA><REQUESTDESC>
<REPORTNAME>Profit and Loss</REPORTNAME>
<STATICVARIABLES>
<SVFROMDATE>${fromDate}</SVFROMDATE>
<SVTODATE>${toDate}</SVTODATE>
<SVCURRENTCOMPANY>${company}</SVCURRENTCOMPANY>
<EXPLODEFLAG>Yes</EXPLODEFLAG>
</STATICVARIABLES>
</REQUESTDESC></EXPORTDATA></BODY></ENVELOPE>`;
  
  const url = getUrl(tallyUrl);
  const response = await axios.post(url, xml, {
    headers: { 'Content-Type': 'application/xml' },
    timeout: TIMEOUT
  });
  return response.data; // Returns raw XML string for parsing by syncEngine
};

const fetchBsData = async (company, fromDate, toDate, tallyUrl) => {
  const xml = `<ENVELOPE>
<HEADER><TALLYREQUEST>Export Data</TALLYREQUEST></HEADER>
<BODY><EXPORTDATA><REQUESTDESC>
<REPORTNAME>Balance Sheet</REPORTNAME>
<STATICVARIABLES>
<SVFROMDATE>${fromDate}</SVFROMDATE>
<SVTODATE>${toDate}</SVTODATE>
<SVCURRENTCOMPANY>${company}</SVCURRENTCOMPANY>
<EXPLODEFLAG>Yes</EXPLODEFLAG>
</STATICVARIABLES>
</REQUESTDESC></EXPORTDATA></BODY></ENVELOPE>`;
  
  const url = getUrl(tallyUrl);
  const response = await axios.post(url, xml, {
    headers: { 'Content-Type': 'application/xml' },
    timeout: TIMEOUT
  });
  return response.data; // Returns raw XML string for parsing by syncEngine
};

// Date Format Helpers (Tally uses YYYYMMDD)
const tallyDate = (date) => {
  const d = new Date(date);
  return d.toISOString().split('T')[0].replace(/-/g, '');
};

module.exports = {
  testConnection,
  getCurrentCompany,
  getAllCompanies,
  fetchPlData,
  fetchBsData,
  tallyDate,
  parser
};
