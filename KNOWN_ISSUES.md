# Known Issues

## Current Limitations

### Docker

- **Image size**: The Docker image may exceed 1.5GB due to Playwright browsers and Python dependencies. Multi-stage builds are planned for future optimization.
- **Windows WSL2**: Volume mounting may have permission issues. Recommended workaround: use WSL2 with the repo in the Linux filesystem (not Windows-mounted paths).
- **GPU support**: NVIDIA GPU passthrough requires manual configuration (see docker-compose.yml comments).

### Ollama

- **Model download time**: First run may take 5-15 minutes to download the default model (`llama3.2:3b`).
- **Memory requirements**: Ollama models need 4-8GB RAM depending on model size. Use `llama3.2:1b` for low-memory systems.

### Legal & Compliance

- **Compliance checker is advisory only**: The `raspal compliance` command provides signals (robots.txt URL, sensitive domain detection) but does not make legal determinations.
- **Stealth mode**: Using stealth/anti-detect features does not make scraping legal. Users are responsible for their actions.

### Platform Support

- **macOS Apple Silicon**: Works with ARM64 Ollama image.
- **macOS Intel**: Works with AMD64 Ollama image.
- **Ubuntu 22.04**: Fully supported.
- **Windows 11 WSL2**: Supported with caveats (see above).

## Planned Fixes

- [ ] Multi-stage Docker build to reduce image size
- [ ] Pre-built images on Docker Hub
- [ ] Better Windows volume handling
- [ ] More comprehensive compliance checks
