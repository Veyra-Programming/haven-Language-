# 📜 Haven & Star Unified Ecosystem Changelog

All notable changes to the **Haven Programming Language**, the **Star Programming Language**, and the **Open Digital Continuity Standard (ODCS)** ecosystem are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [3.0.0 GA] - 2026-11-18 (Ani++ OmniEngine, World-First Causality & All-Field Superpowers Milestone)

### 🌟 Highlights & Major Breakthroughs
- **Ani++ Dual-Identity Engine**:
  - The language now operates with full dual identity as **Ani++** and **Haven** interchangeably across executables, scripts, CLI commands, and runtime namespaces (`haven` and `ani`).
  - Native binary entrypoints: `ani.exe`, `ani.bat`, `haven.exe`, `haven.bat`.
  - Python runtime namespace reflects `sys.implementation.name = 'ani++'`.
- **4 World-First Computational Architectures (Ani++ OmniEngine)**:
  - **4D Chrono-Quantum Causality DAG & Timeline Rewind (`ChronoEngine`)**: Non-linear causality directed acyclic graph allowing timelines to rewind, branch, and merge while maintaining tamper-proof Merkle commit proofs.
  - **Polymorphic Entangled Memory Fabric (`RealityState`)**: Variables interconnected across memory spaces where state changes trigger bidirectional wave mutations (`EntangledVariable`, `SynthesizedVariable`, `DurableVariable`).
  - **Autonomous Living Intent Healer Reactor (`AutonomousHealer`)**: Active self-healing runtime that intercepts panics, invariant breaches, and crashes, synthesizing healing strategies (`HEAL_ROLLBACK`, `HEAL_COMPENSATE`, `HEAL_SYNTHESIZE`) and minting cryptographic audit receipts.
  - **Cognitive Synthesis Semantic Search Reactor (`CognitiveReactor`)**: Zero-dependency 512-dimensional deterministic vector embeddings and cosine nearest-neighbor document retrieval.
- **Industrial All-Field Superpowers**:
  - **Scientific Computing & Linear Algebra (`ani.scientific` / `haven.scientific`)**: High-precision `Matrix` linear algebra (matrix multiplication `@`, Gauss-Jordan inversion, determinants with partial pivoting, transpositions, traces), 1D `Series`, and in-memory columnar `DataFrame` (predicate filtering `where`/`filter`, column projections, summary statistics, CSV export).
  - **Robotics & Cyber-Physical Telemetry (`ani.robotics` / `haven.robotics`)**: Industrial real-time `PIDController` with anti-windup clamping, discrete 1D `KalmanFilter` for Gaussian noise filtering, and O(1) streaming `CircularRingBuffer`.
  - **Zero-Trust Cyber Defense & Consensus (`ani.cyber` / `haven.cyber`)**: `CyberVault` AES/HMAC-SHA256 authenticated envelope encryption with rotating salt and anti-tamper verification, `ByzantineConsensus` (PBFT 4-phase state engine tolerating up to $f < N/3$ malicious nodes), and `SandboxedProcess` execution with SHA-256 audit receipts.
- **Comprehensive Cryptography & Ciphers Suite (`haven.crypto` / `ani.crypto`)**:
  - **Classical Transposition & Substitution**: `RailFenceCipher` (zig-zag transposition with arbitrary rails), `ColumnarTranspositionCipher` (keyed single & double transposition), `CaesarCipher`, `VigenereCipher`, `PlayfairCipher` (5x5 matrix bigrams), `AffineCipher`, `AtbashCipher`, and `PolybiusSquare`.
  - **Modern Cryptography**: `FeistelCipher` (16-round symmetric block cipher with PKCS7 padding), `DiffieHellman` discrete logarithm key agreement, and `ShamirSecretSharing` $(k, n)$ threshold polynomial secret splitting over a 256-bit prime field.
  - **World-First Invented Cipher: Haven Continuum Cipher (CQE-512)**:
    - Chrono-quantum entangled cipher featuring 4D temporal epoch binding, Merkle-derived dynamic S-Box (MD-SBox), hyper-rail 4D multi-dimensional transposition, lattice vector perturbation, and ODCS HMAC-SHA256 zero-intent-loss integrity seals.
- **Strict Separation of Concerns between Star and Haven**:
  - Maintained distinct architectural boundaries: Star remains the specialized Flutter/declarative mobile UI layer, while Haven/Ani++ is the high-performance systems, causality, scientific, cyber, and continuity engine.
- **Standalone Distribution & Native Windows Setup EXE**:
  - Assembled `Haven-3.0.0-GA-win64` portable runtime and compiled native standalone setup installer `Haven-3.0.0-GA-Setup.exe` with C# and embedded ZIP archive.
- **100% Test Conformance**:
  - All 22 test suites running 100% green in 2.75 seconds.

---

## [2.1.1 GA] - 2026-11-17 (General Availability Milestone)

### 🌟 Highlights & Major Breakthroughs
- **Unified Single-Directory Architecture**: Haven and Star now operate harmoniously within a single workspace directory (`E:\Heaven Language`).
- **First-Class Initial Packages (`hvn` and `str`)**:
  - `use hvn` / `import hvn` / `import Hvn`: Instant access to all ODCS, OFCS, Living Intent, and 200+ standard library methods.
  - `use str` / `import str` / `import star`: Instant access to Star's Zero-JS Flutter declarative UI, Android hardware services, and StarVM.
- **Callable `str` Namespace Preservation**:
  - Implemented the `_StarMeta` metaclass and `StarPackage(builtins.str)` pattern.
  - Eliminates namespace collisions between the Star language module and Python/Haven built-in `str(...)` string type conversion, allowing `isinstance(x, str)`, `str(12345)`, and `str.Scaffold(...)` to coexist cleanly.
- **Sovereign Package Manager for `odcshosting.in`**:
  - Integrated CLI tooling for `https://api.odcshosting.in/v1`.
  - Package publishing, search, verification, and tamper-proof `haven.lock` manifest generation.
  - Built-in lightweight self-hosted package registry server (`haven pkg serve`).
- **Unified Root Batch Launchers**:
  - `hvn.bat`: Direct Haven CLI entrypoint.
  - `str.bat` and `star.bat`: Direct Star compiler & native execution entrypoint.
- **100% Conformance Validation**: All 19 test suites passing green across ODCS, OFCS, UI, package management, and multi-language interop.

---

### 🚀 Added
#### 1. Single-Directory Multi-Language Gateway
- `Lib/hvn/__init__.py`: Primary initial import gateway for Haven, exposing `hvn.units`, `hvn.intent`, `hvn.methods`, `hvn.flow`, `hvn.neural`, `hvn.iot`, `hvn.zk`, `hvn.agents`, `hvn.continuity`, and `hvn.algorithm`.
- `Lib/str/__init__.py`: Primary initial import gateway for Star, implementing callable string inheritance alongside declarative UI and hardware APIs.
- `Lib/star/__init__.py`: First-class alias for the `str` package.
- `Lib/Flutter/__init__.py` & `Lib/Material/__init__.py`: Direct compatibility packages for Star Flutter apps.
- `Lib/sitecustomize.py`: Dynamic casing and aliasing meta-path finder for `Hvn`, `Flutter`, and `Material`.

#### 2. Star Declarative UI Subsystem (`Lib/str/ui.py`)
- **Structural Widgets**: `Scaffold`, `AppBar`, `BottomNavigationBar`, `FloatingActionButton`, `SafeArea`.
- **Layout Widgets**: `Column`, `Row`, `Stack`, `Positioned`, `Container`, `Padding`, `Center`, `Expanded`, `SizedBox`, `Wrap`, `Spacer`.
- **Interactive Widgets**: `GestureDetector`, `ElevatedButton`, `InkWell`, `CupertinoButton`, `IconButton`.
- **Content Widgets**: `Text`, `Image` (`Image.network`, `Image.asset`), `Icon`, `Card`, `ListView` (`ListView.builder`), `GridView`.
- **Conditional Widgets**: `When`, `SwitchCase`, `Visibility`, `Opacity`.
- **Styling & Theming**: `Color`, `Colors`, `Icons`, `TextStyle`, `FontWeight`, `EdgeInsets`, `BorderRadius`, `BoxDecoration`, `BoxShadow`, `LinearGradient`, `MainAxisAlignment`, `CrossAxisAlignment`, `BoxFit`.
- Terminal User Interface (TUI) layout renderer via `Widget.render_tui()`.

#### 3. Native Mobile & Hardware Subsystem (`Lib/str/mobile.py`)
- `AndroidWallpaperService`: Home/Lock screen wallpaper configuration, parallax assets, and history audit tracking.
- `AndroidHapticService`: Vibration, impact feedback (`light`, `medium`, `heavy`), and click events.
- `Mobile.Hardware`: Unified Gyroscope sensors (`listenGyroscope`), Battery metrics, and System Clipboard.
- `GoogleBillingClient`: Google Play Billing v7.0.0 lifecycle, product purchasing, and subscription checks.

#### 4. Star VM & Compiler Bridge (`Lib/str/vm.py`)
- `StarApp`: Declarative application base class.
- `StarVM`: Toolchain bridge detecting local native PE launcher (`star.exe`) or simulating execution.

#### 5. Sovereign Package Management (`Lib/haven/pkg/`)
- Client support for `odcshosting.in` (`DEFAULT_REGISTRY_URL = "https://api.odcshosting.in/v1"`).
- Commands: `haven pkg init`, `haven pkg search <q>`, `haven pkg info <pkg>`, `haven pkg install <pkg>`, `haven pkg publish <pkg>`, `haven pkg serve`.
- Lockfile engine: Generates deterministic `haven.lock` tracking SHA-256 integrity digests for all installed packages.

#### 6. 200+ Standard Library Methods (`Lib/haven/methods/`)
- **Math & Statistics**: `clamp`, `lerp`, `mean`, `median`, `variance`, `std_dev`, `factorial`, `gcd`, `lcm`, `hypot`, `degrees`, `radians`, `moving_average`.
- **String & Text (NLP)**: `slugify`, `camel_case`, `snake_case`, `kebab_case`, `pascal_case`, `title_case`, `truncate_words`, `word_count`, `levenshtein_distance`, `soundex`, `pad_center`, `reverse_string`, `rot13`.
- **Collections & Functional**: `chunk`, `flatten`, `unique`, `compact`, `partition`, `key_by`, `group_by_key`, `frequency_map`, `zip_longest_fill`, `interleave`, `windowed`.
- **Chrono & Timestamps**: `now_iso`, `now_unix_ms`, `is_leap_year`, `days_in_month`, `format_duration_ms`, `date_add_days`, `date_diff_days`.
- **Cryptography & Security**: `sha256_hex`, `sha512_hex`, `sha3_256_hex`, `sha3_512_hex`, `hmac_sha256_hex`, `hmac_sha512_hex`, `pbkdf2_hash_hex`, `mask_hash`, `hash_file_sha256`.
- **File System & Paths**: `safe_read_text`, `safe_write_text`, `ensure_dir`, `list_files_ext`, `file_size_human`, `path_is_safe`.
- **System & Runtime**: `get_env_default`, `haven_system_diagnostics`, `measure_execution_time`.

#### 7. Universal Living Intent Fabric (ULIF) & Dimensional Safety
- `Lib/haven/intent.py`: `IntentContract`, `LivingReceipt`, `@living_intent`, `execute_intent`.
- `Lib/haven/units.py`: Universal Dimensional Safety Engine (`meters`, `seconds`, `kilograms`, `megabytes`).
- Added `.value` alias property to `UnitQuantity`.

#### 8. Verification Suites
- `tests/test_hvn_and_str_single_dir.hvn`: End-to-end verification of `use hvn` and `use str` coexisting in a single directory.
- `tests/test_odcshosting_pkg.hvn`: Complete package manager verification suite.
- `tests/test_100_methods.hvn`: Comprehensive standard method suite across all 7 categories.

---

### 🛡️ Changed & Improved
- Upgraded system version to **`Haven 2.1.1 GA`** in `Lib/haven/__init__.py`, `Lib/haven/cli/main.py`, `Lib/haven/cli/repl.py`, and `Lib/haven/cli/builder.py`.
- Formatted and refreshed root CLI banners for interactive and terminal execution.
- License & Governance: Updated to **Haven Global Public License & Digital Continuity Charter (H-GPL / ODCS-OSL v2.0)** authored by Anirudha Puthraya.
- Eliminated all legacy third-party branding in installers and CLI documentation, linking institutional edge nodes to `https://api.odcs.in`.

---

## [2.0.0 GA] - 2026-11-01
- Major release introducing ODCS 2.0 with tamper-evident Merkle DAG roots and sub-16ms local authority receipts.
- Implemented Open Financial Continuity Standard (OFCS) double-entry ledger balance enforcement.
- Introduced Autonomous Living Agent Mesh (ALAM) and Zero-Knowledge Range Proofs (ZK-ODCS).
- Added Reactive Living Streams (HavenFlow) and Neural Thought Graphs (HavenNeural).

---

## [1.0.0] - 2026-10-15
- Initial public release of Haven Programming Language.
- Core C-Parser natural English grammar (`set ... to`, `whenever ... otherwise`, `give back`, `ensure ... otherwise`).
- ODCS 4-layer continuity architecture and local write-ahead ledger (WAL).
