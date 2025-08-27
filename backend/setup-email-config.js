const fs = require('fs');
const path = require('path');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

console.log('📧 Email Configuration Setup');
console.log('============================\n');

// Read the example env file
const envExamplePath = path.join(__dirname, 'env.example');
const envPath = path.join(__dirname, '.env');

if (!fs.existsSync(envExamplePath)) {
  console.error('❌ env.example file not found!');
  process.exit(1);
}

// Read env.example content
const envExampleContent = fs.readFileSync(envExamplePath, 'utf8');

// Function to ask for email configuration
const askEmailConfig = () => {
  return new Promise((resolve) => {
    console.log('🔧 Email Configuration Setup\n');
    
    rl.question('Enter your Gmail address: ', (email) => {
      rl.question('Enter your Gmail App Password (not regular password): ', (password) => {
        resolve({ email, password });
      });
    });
  });
};

// Function to create .env file
const createEnvFile = (emailConfig) => {
  let envContent = envExampleContent;
  
  // Replace email configuration
  envContent = envContent.replace(/EMAIL_USER=your_email@gmail.com/g, `EMAIL_USER=${emailConfig.email}`);
  envContent = envContent.replace(/EMAIL_PASS=your_app_password/g, `EMAIL_PASSWORD=${emailConfig.password}`);
  envContent = envContent.replace(/EMAIL_FROM=your_email@gmail.com/g, `EMAIL_FROM=${emailConfig.email}`);
  
  // Write to .env file
  fs.writeFileSync(envPath, envContent);
  
  console.log('\n✅ .env file created successfully!');
  console.log(`📧 Email configured: ${emailConfig.email}`);
};

// Main setup function
const setupEmail = async () => {
  try {
    console.log('📋 Instructions:');
    console.log('1. You need a Gmail account');
    console.log('2. Enable 2-Factor Authentication on your Google account');
    console.log('3. Generate an App Password:');
    console.log('   - Go to Google Account → Security → App passwords');
    console.log('   - Select "Mail" and your device');
    console.log('   - Copy the generated password\n');
    
    const emailConfig = await askEmailConfig();
    
    if (!emailConfig.email || !emailConfig.password) {
      console.log('❌ Email and password are required!');
      rl.close();
      return;
    }
    
    createEnvFile(emailConfig);
    
    console.log('\n🎉 Email configuration complete!');
    console.log('\n📝 Next steps:');
    console.log('1. Restart your backend server');
    console.log('2. Test email configuration with: node test-email.js');
    console.log('3. Check that "📧 Email service: ✅ Enabled" appears in server logs');
    
  } catch (error) {
    console.error('❌ Setup failed:', error.message);
  } finally {
    rl.close();
  }
};

// Run setup
setupEmail();
