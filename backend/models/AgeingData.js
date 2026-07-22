const mongoose = require('mongoose');

const ageingDataSchema = new mongoose.Schema({
  company: { type: mongoose.Schema.Types.ObjectId, ref: 'Company', required: true },
  party_type: { type: String, required: true },
  party_name: { type: String, required: true },
  bill_ref: { type: String },
  bill_date: { type: String },
  due_date: { type: String },
  amount: { type: Number, default: 0 },
  days_overdue: { type: Number, default: 0 },
  synced_at: { type: String }
});

ageingDataSchema.index({ company: 1, party_type: 1 });

module.exports = mongoose.model('AgeingData', ageingDataSchema);
