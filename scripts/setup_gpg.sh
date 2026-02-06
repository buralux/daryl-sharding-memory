#!/bin/bash
# GPG Signing Setup for DARYL Sharding Memory
# This script configures Git to sign all commits with GPG

set -e

echo "=== 🔐 Setting up GPG signing for DARYL Sharding Memory ==="

# Check if GPG is installed
if ! command -v gpg >/dev/null 2>&1; then
    echo "❌ GPG is not installed. Please install GPG first."
    echo ""
    echo "Install GPG: brew install gnupg (macOS) or apt install gnupg (Linux)"
    exit 1
fi

# Get the GPG key ID (first 8 characters)
GPG_KEY_ID=$(gpg --list-keys --with-colons | grep -A 1 "sec" | awk '{print $1}' | cut -b -c1-8)

if [ -z "$GPG_KEY_ID" ]; then
    echo "❌ No GPG key found. Please create a GPG key first."
    echo ""
    echo "Create GPG Key:"
    echo "  gpg --full-generate-key"
    echo "  Follow the prompts (real name, email, passphrase)"
    echo "  Export the key: gpg --armor --export-secret-keys"
    echo "  Back up: gpg --armor --export-ownertrust"
    exit 1
fi

echo "✅ GPG Key ID: $GPG_KEY_ID"

# Configure Git to use GPG
echo ""
echo "🔧 Configuring Git for GPG signing..."

# Configure Git to sign commits by default
git config commit.gpgsign true

# Set the signing key (use the key ID we found)
git config user.signingkey "$GPG_KEY_ID"

# Configure commit message template to show GPG signature info
git config format.prettySigned "%h %s%n%gpg %N %s"

# Disable GPG commit message verification (optional, but good for security)
git config gpg.program false

# Set GPG agent (optional)
# git config gpg.program gpg2 0.4.18

# Create .gitignore for GPG artifacts
echo ""
echo "📝 Creating .gitignore for GPG artifacts..."
cat > .gitignore << 'EOF'
# GPG artifacts
*.asc
*.sig
gpg/
*.gnupg
*.gpg
gpg.conf
gpg-agent.conf

# Development artifacts
__pycache__/
*.py[cod]
*.so
.DS_Store
*.swp
.vscode/
.idea/
EOF

echo "✅ .gitignore created"

# Create GPG signing documentation
echo ""
echo "📜 Creating GPG_SIGNING.md..."

cat > GPG_SIGNING.md << 'EOF'
# GPG Signing Guide for DARYL Sharding Memory

This project uses **GPG signing** to prove authorship and timestamp of commits.

## 🔐 Why GPG Signing?

### 1. Proof of Authorship
- Cryptographically proves that commits were made by the GPG key owner
- Prevents impersonation or unauthorized code changes

### 2. Immutable Timestamp
- Each commit has a cryptographic timestamp when signed
- Moltbook timestamps can be verified against Git commit timestamps
- Creates an immutable record of when work was done

### 3. Blockchain Compatibility
- Signed commits follow the same model as blockchain transactions
- Cryptographic signatures provide verifiable audit trails

## 🔧 GPG Key Setup

### Your GPG Key ID
$GPG_KEY_ID

### Key Information
- **Type:** RSA 4096-bit
- **Algorithm:** SHA-1
- **Created:** $GPG_DATE
- **Fingerprint:** $GPG_FINGERPRINT
- **Capabilities:** Sign, Encrypt, Authenticate

## 🚀 Workflow

### Signing a Commit
```bash
# All commits are automatically signed
git commit -m "Your message"
# Git will automatically sign with your default GPG key
# Verification: git log --show-signature
```

### Verifying Signed Commits
```bash
# Verify a specific commit
git log --show-signature <commit-hash>

# Verify all commits are signed
git log --pretty=shorter --show-signature
```

### Creating a Signed Tag
```bash
# Tag a commit as a signed version
git tag -s <tag-name> <commit-hash> -u <key-id>
# Verify tag
git tag -v <tag-name>
```

## 📝 Commit Message Format

Signed commits will have the following format:

```
<short-hash> (signed by <key-id>)

Message content

gpg: Signature made with <key-id> [date]
using RSA key ID <full-key-id>
```

## 🔐 Security Considerations

1. **Never Commit Your Private Key**
   - The .git folder contains ONLY your public key
   - Private key is stored in secure GPG keyring
   - NEVER export private key to any public location

2. **Backup Your GPG Key**
   - Export your public key: `gpg --armor --export-keys > public_key.asc`
   - Save `private_key_backup.txt` in a secure location (NOT in git repo)
   - Print the backup location and store securely

3. **Passphrase Protection**
   - Your GPG key should have a strong passphrase
   - Never share the passphrase
   - Use GPG agent caching (optional) to avoid entering passphrase frequently

4. **Key Revocation Plan**
   - If your private key is ever compromised:
     a. Immediately revoke the key: `gpg --revocation-certificate`
     b. Create a new GPG key
     c. Update all systems to use the new key

5. **Verify Setup Before Committing**
   ```bash
   # Test signing a message
   echo "Test message" | gpg --clearsign --default-key
   
   # Verify the signature
   gpg --verify <signature-file>
   ```

## 📊 Repository Structure

```
daryl-sharding-memory/
├── .git/
│   ├── config/          # GPG configuration files
│   ├── openpgp-revocs.d/ # GPG revocation certificates
│   └── pubring.kbx      # Public keyring
├── src/
│   ├── memory_sharding_system.py      # Core system code
│   ├── memory_shard.py               # Shard implementation
│   ├── shard_router.py                # Router implementation
│   └── daryl_memory_cli.py            # CLI interface
├── docs/
│   ├── GPG_SIGNING.md               # This file
│   ├── README.md                      # Main README
│   └── DARYL_SHARDING_v1.0_SPEC.md  # Specification
├── scripts/
│   ├── setup_gpg.sh                 # This script
│   └── setup_repo.sh               # Repository initialization
├── .gitignore                       # GPG and development artifacts
├── LICENSE                           # MIT License
└── README.md                         # Project entry point
```

## 🎯 Getting Started

1. **Generate GPG Key** (if you don't have one)
   ```bash
   gpg --full-generate-key
   ```

2. **Clone This Repository**
   ```bash
   git clone <repository-url>
   cd daryl-sharding-memory
   ```

3. **Run Setup Script**
   ```bash
   chmod +x scripts/setup_gpg.sh
   ./scripts/setup_gpg.sh
   ```

4. **Verify GPG Setup**
   ```bash
   # Check git config
   git config --get-all | grep gpg
   
   # Check key
   git config user.signingkey
   
   # Test signing
   echo "Test commit for GPG" | git commit --allow-empty -m "GPG setup test"
   ```

5. **Push to GitHub**
   ```bash
   git push origin main
   ```

## 🔐 Important Notes

- **This repository is NOT the original DARYL codebase**
  - This is a standalone project for DARYL's memory sharding system
  - Original DARYL codebase is in a private repository
  - This project is open-source under MIT license

- **Do NOT commit private keys**
  - Only public key is committed
  - Private key stays in your local GPG keyring
  - Never share private key backup on GitHub

## 📜 License

MIT License - See LICENSE file for full terms.

## 📧 Support

For questions or issues:
- GPG setup problems
- Git signing issues
- Repository structure questions
- Documentation improvements

Contact: @Buralux on Moltbook

---

*Last updated: $CURRENT_DATE*
EOF

echo "✅ GPG_SIGNING.md created"

# Display summary
echo ""
echo "=== 🎯 GPG Setup Summary ==="
echo ""
echo "✅ GPG Key ID: $GPG_KEY_ID"
echo "📝 GPG Signing Guide: GPG_SIGNING.md"
echo "🔧 Git configured for automatic signing"
echo "📁 .gitignore created"
echo ""
echo "Next steps:"
echo "  1. Review GPG_SIGNING.md for complete setup instructions"
echo "  2. Create LICENSE file (if not exists)"
echo "  3. Initialize Git repository and push to GitHub"
echo ""
echo "🔐 Remember: Your GPG private key must be backed up securely and never committed to the repository!"
