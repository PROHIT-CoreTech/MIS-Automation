const mongoose = require('mongoose');

const companySchema = new mongoose.Schema({
  tenant: { type: mongoose.Schema.Types.ObjectId, ref: 'Tenant', required: true },
  tally_name: { type: String, required: true },
  display_name: { type: String },
  company_type: { type: String, default: 'STANDARD' },
  books_from: { type: String },
  last_full_sync: { type: String },
  last_sync: { type: String },
  sync_status: { type: String, default: 'pending' },
  is_active: { type: Boolean, default: true },
  created_at: { type: Date, default: Date.now }
}, { collection: 'company' });

companySchema.index({ tenant: 1, tally_name: 1 }, { unique: true });

module.exports = mongoose.model('Company', companySchema, 'company');
