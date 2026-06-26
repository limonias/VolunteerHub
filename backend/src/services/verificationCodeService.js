const crypto = require('crypto');
const mongoose = require('mongoose');

const verificationCodeSchema = new mongoose.Schema({
  email: { type: String, required: true, lowercase: true, trim: true },
  codeHash: { type: String, required: true },
  expiresAt: { type: Date, required: true },
  createdAt: { type: Date, default: Date.now },
});

verificationCodeSchema.index({ expiresAt: 1 }, { expireAfterSeconds: 0 });
verificationCodeSchema.index({ email: 1 });

const VerificationCode = mongoose.model('VerificationCode', verificationCodeSchema);

function generateCode() {
  const number = crypto.randomInt(0, 1_000_000);
  return String(number).padStart(6, '0');
}

function hashCode(code) {
  return crypto.createHash('sha256').update(code).digest('hex');
}

const OTP_EXPIRY_MINUTES = Number(process.env.OTP_EXPIRY_MINUTES) || 10;

async function createVerificationCode(email) {
  await VerificationCode.deleteMany({ email: email.toLowerCase() });
  const code = generateCode();
  const expiresAt = new Date(Date.now() + OTP_EXPIRY_MINUTES * 60 * 1000);
  await VerificationCode.create({ email: email.toLowerCase(), codeHash: hashCode(code), expiresAt });
  return code;
}

async function verifyCode(email, submittedCode) {
  const record = await VerificationCode.findOne({ email: email.toLowerCase() });
  if (!record) return { success: false, reason: 'No verification code found for this email.' };
  if (record.expiresAt < new Date()) {
    await record.deleteOne();
    return { success: false, reason: 'Verification code has expired.' };
  }
  const submittedHash = hashCode(submittedCode.trim());
  const isMatch = crypto.timingSafeEqual(
    Buffer.from(record.codeHash, 'hex'),
    Buffer.from(submittedHash, 'hex')
  );
  if (!isMatch) return { success: false, reason: 'Invalid verification code.' };
  await record.deleteOne();
  return { success: true };
}

async function deleteCodesForEmail(email) {
  await VerificationCode.deleteMany({ email: email.toLowerCase() });
}

module.exports = { createVerificationCode, verifyCode, deleteCodesForEmail };
