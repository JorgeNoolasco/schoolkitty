const crypto = require('node:crypto');
const readline = require('node:readline');
if (!process.stdin.isTTY || !process.stdin.setRawMode) {
  console.error('Execute este comando em um terminal interativo para ocultar a senha digitada.');
  process.exit(1);
}
readline.emitKeypressEvents(process.stdin);
process.stdin.setRawMode(true);
process.stdout.write('Senha administrativa (mínimo 12 caracteres): ');
let password = '';
process.stdin.on('keypress', (character, key) => {
  if (key && key.ctrl && key.name === 'c') { process.stdout.write('\n'); process.exit(130); }
  if (key && key.name === 'return') {
    process.stdout.write('\n'); process.stdin.setRawMode(false); process.stdin.pause();
    if (password.length < 12) { console.error('A senha precisa ter pelo menos 12 caracteres.'); process.exit(1); }
    const salt = crypto.randomBytes(16).toString('hex');
    const hash = crypto.scryptSync(password, salt, 64).toString('hex');
    password = '';
    console.log(`scrypt$${salt}$${hash}`);
    return;
  }
  if (key && key.name === 'backspace') password = password.slice(0, -1);
  else if (!key || !key.ctrl && !key.meta) password += character;
});
