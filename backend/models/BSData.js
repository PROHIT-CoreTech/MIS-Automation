const mongoose = require('mongoose');

const bsDataSchema = new mongoose.Schema({
  company: { type: mongoose.Schema.Types.ObjectId, ref: 'Company', required: true },
  ledger_name: { type: String, required: true },
  tally_group: { type: String },
  mis_group: { type: String },
  year: { type: Number, required: true },
  month: { type: Number, required: true },
  month_label: { type: String },
  closing_bal: { type: Number, default: 0 },
  updated_at: { type: Date, default: Date.now }
});

bsDataSchema.index({ company: 1, ledger_name: 1, year: 1, month: 1 }, { unique: true });
bsDataSchema.index({ company: 1, year: 1, month: 1 });

module.exports = mongoose.model('BSData', bsDataSchema, 'b_s_data');
