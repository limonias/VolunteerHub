const express = require('express');
const router = express.Router();
const { createVerificationCode, verifyCode, deleteCodesForEmail } = require('../services/verificationCodeService');
const { sendVerificationEmail } = require('../services/emailService');

router.post('/send-code', async (req, res) => {
  const { email } = req.body;
  if (!email) return res.status(400).json({ error: 'Email is required.' });
  try {
    const code = await createVerificationCode(email);
    await sendVerificationEmail(email, code);
    return res.status(200).json({ message: 'Verification code sent.' });
  } catch (err) {
    console.error('[send-code]', err);
    return res.status(500).json({ error: 'Failed to send verification code.' });
  }
});

router.post('/verify-code', async (req, res) => {
  const { email, code } = req.body;
  if (!email || !code) return res.status(400).json({ error: 'Email and code are required.' });
  try {
    const result = await verifyCode(email, code);
    if (!result.success) return res.status(400).json({ error: result.reason });
    return res.status(200).json({ message: 'Email verified successfully.' });
  } catch (err) {
    console.error('[verify-code]', err);
    return res.status(500).json({ error: 'Verification failed.' });
  }
});

router.post('/resend-code', async (req, res) => {
  const { email } = req.body;
  if (!email) return res.status(400).json({ error: 'Email is required.' });
  try {
    await deleteCodesForEmail(email);
    const code = await createVerificationCode(email);
    await sendVerificationEmail(email, code);
    return res.status(200).json({ message: 'A new verification code has been sent.' });
  } catch (err) {
    console.error('[resend-code]', err);
    return res.status(500).json({ error: 'Failed to resend verification code.' });
  }
});

module.exports = router;
