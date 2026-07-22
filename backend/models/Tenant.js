const mongoose = require('mongoose');

const tenantSchema = new mongoose.Schema({
  name: { type: String, required: true },
  slug: { type: String, required: true, unique: true },
  plan_name: { type: String, default: 'Silver' },
  is_active: { type: Boolean, default: true },
  features: { type: mongoose.Schema.Types.Mixed, default: [] },
  tally_url: { type: String, default: 'http://localhost:9000' },
  created_at: { type: Date, default: Date.now },
  updated_at: { type: Date, default: Date.now }
}, { collection: 'tenant', strict: false });

// Update updated_at on every save
tenantSchema.pre('save', function (next) {
  this.updated_at = Date.now();
  next();
});

module.exports = mongoose.model('Tenant', tenantSchema, 'tenant');
