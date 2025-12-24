Static analysis findings (initial pass):

- Potentially risky API uses found (files with network or shell):
  - convict_project_creator.py: uses subprocess (line ~20)
  - Many modules use aiohttp for network requests (agents, utilities)
  - agent_zero_framework/helpers/shell_ssh.py: paramiko SSH client
  - tts/rsi generator uses external HTTP image APIs (rsi_generator.py)

- Serialization / file handling:
  - YAML loading uses safe_load in many places but check for any yaml.load without SafeLoader
  - Soul anchor ledger reads and writes binary files; ensure signature checks are robust

- Dynamic execs/pickle:
  - No use of eval/exec detected in codebase scan, but many files write and read JSON/YAML and execute shell commands (careful with untrusted inputs)

- Tests with network dependencies present; will request permission before running

Next steps:
- Produce SECURITY_PRIVACY_RISKS.md detailing each area with remediation suggestions
- Continue reading and summarizing research-whitepapers
