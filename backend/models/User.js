const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  tenant: { type: mongoose.Schema.Types.ObjectId, ref: 'Tenant' },
  username: { type: String, required: true, unique: true },
  password_hash: { type: String, required: true },
  full_name: { type: String, required: true },
  role: { type: String, enum: ['super_admin', 'admin', 'user', 'client'], default: 'user' },
  can_download_excel: { type: Boolean, default: true },
  can_download_ppt: { type: Boolean, default: false },
  is_active: { type: Boolean, default: true },
  failed_attempts: { type: Number, default: 0 },
  companies: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Company' }],
  created_at: { type: Date, default: Date.now }
}, { collection: 'user' });

module.exports = mongoose.model('User', userSchema, 'user');
