const nodemailer = require('nodemailer');

const transporter = nodemailer.createTransport({
  host: process.env.EMAIL_HOST,
  port: Number(process.env.EMAIL_PORT) || 587,
  secure: process.env.EMAIL_PORT === '465',
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASS,
  },
});

const OTP_EXPIRY_MINUTES = Number(process.env.OTP_EXPIRY_MINUTES) || 10;

function buildEmailHtml(code) {
  return `
  <div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;">
    <div style="background:#2d6a4f;padding:24px;border-radius:8px 8px 0 0;">
      <h1 style="color:#fff;margin:0;">🌱 Dobrodiy</h1>
    </div>
    <div style="background:#fff;padding:32px;border:1px solid #eee;">
      <h2 style="color:#1b1b1b;">Verify your email address</h2>
      <p style="color:#555;">Your verification code (valid for ${OTP_EXPIRY_MINUTES} minutes):</p>
      <div style="text-align:center;margin:24px 0;">
        <span style="background:#f0f7f4;border:2px solid #2d6a4f;border-radius:8px;
                     padding:16px 40px;font-size:36px;font-weight:700;
                     letter-spacing:10px;color:#2d6a4f;">
          ${code}
        </span>
      </div>
      <p style="color:#888;font-size:13px;">If you did not create a Dobrodiy account, ignore this email.</p>
    </div>
  </div>`;
}

async function sendVerificationEmail(toEmail, code) {
  await transporter.sendMail({
    from: process.env.EMAIL_FROM || '"Dobrodiy" <no-reply@dobrodiy.org>',
    to: toEmail,
    subject: `${code} is your Dobrodiy verification code`,
    text: `Your verification code: ${code}. Valid for ${OTP_EXPIRY_MINUTES} minutes.`,
    html: buildEmailHtml(code),
  });
}

async function verifyTransporter() {
  try {
    await transporter.verify();
    return true;
  } catch {
    return false;
  }
}

module.exports = { sendVerificationEmail, verifyTransporter };
