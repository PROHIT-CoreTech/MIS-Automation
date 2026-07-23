const mongoose = require('mongoose');

const plDataSchema = new mongoose.Schema({
  company: { type: mongoose.Schema.Types.ObjectId, ref: 'Company', required: true },
  ledger_name: { type: String, required: true },
  tally_group: { type: String },
  mis_group: { type: String },
  year: { type: Number, required: true },
  month: { type: Number, required: true },
  month_label: { type: String },
  debit: { type: Number, default: 0 },
  credit: { type: Number, default: 0 },
  net: { type: Number, default: 0 },
  updated_at: { type: Date, default: Date.now }
});

plDataSchema.index({ company: 1, ledger_name: 1, year: 1, month: 1 }, { unique: true });
plDataSchema.index({ company: 1, year: 1, month: 1 });

module.exports = mongoose.model('PLData', plDataSchema, 'p_l_data');
