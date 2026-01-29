# 自定义服务器构建指南

本文档说明如何构建带有自定义 RustDesk 服务器配置的客户端。

## 问题修复说明

此版本修复了使用自建服务器时出现 "Failed to secure tcp: deadline has elapsed" 错误的问题。

### 问题原因
之前的代码错误地使用 `access_token`（API 服务器认证令牌）来判断是否需要对会合服务器连接进行加密握手。当用户登录了 RustDesk API 账号后，即使使用自建服务器也会尝试加密握手，导致超时。

### 修复内容
- `src/ui_session_interface.rs`: 移除了错误的 `access_token` 使用
- `build.rs`: 添加了从环境变量读取自定义服务器配置的功能
- `src/platform/windows.rs`: 优先使用编译时嵌入的服务器配置

## 配置格式

自定义服务器配置字符串示例：
```
==Qfi0zdHdlVBdWe4sCc4FHaiNlMqNkaQF1ZxgVMDZHOlZ3dBVVVJV0boNXYzgTNiojI5V2aiwiIyVmdyV2ctkGch1yazVGZ0NXdy9CcvRnLzVXbzhmL09yL6MHc0RHaiojIpBXYiwiI3ETMxIjOw9GduMXdtNHauQnI6ISehxWZyJCLiYTMxEjM6A3b05yc112co5CdiojI0N3boJye
```

此配置字符串包含：
- 服务器地址 (host)
- 服务器密钥 (key)
- API 服务器地址 (api，可选)
- 中继服务器地址 (relay，可选)

## 本地构建

### Windows

```powershell
# 设置环境变量
$env:RUSTDESK_CUSTOM_SERVER="==Qfi0zdHdlVBdWe4sCc4FHaiNlMqNkaQF1ZxgVMDZHOlZ3dBVVVJV0boNXYzgTNiojI5V2aiwiIyVmdyV2ctkGch1yazVGZ0NXdy9CcvRnLzVXbzhmL09yL6MHc0RHaiojIpBXYiwiI3ETMxIjOw9GduMXdtNHauQnI6ISehxWZyJCLiYTMxEjM6A3b05yc112co5CdiojI0N3boJye"

# Flutter 版本（推荐）
python build.py --portable --hwcodec --flutter --vram

# Sciter 版本
cargo build --release --features inline
```

### macOS

```bash
# 设置环境变量
export RUSTDESK_CUSTOM_SERVER="==Qfi0zdHdlVBdWe4sCc4FHaiNlMqNkaQF1ZxgVMDZHOlZ3dBVVVJV0boNXYzgTNiojI5V2aiwiIyVmdyV2ctkGch1yazVGZ0NXdy9CcvRnLzVXbzhmL09yL6MHc0RHaiojIpBXYiwiI3ETMxIjOw9GduMXdtNHauQnI6ISehxWZyJCLiYTMxEjM6A3b05yc112co5CdiojI0N3boJye"

# Flutter 版本
python3 build.py --flutter --hwcodec

# 直接构建
cargo build --release --features flutter,hwcodec
```

### Linux

```bash
# 设置环境变量
export RUSTDESK_CUSTOM_SERVER="==Qfi0zdHdlVBdWe4sCc4FHaiNlMqNkaQF1ZxgVMDZHOlZ3dBVVVJV0boNXYzgTNiojI5V2aiwiIyVmdyV2ctkGch1yazVGZ0NXdy9CcvRnLzVXbzhmL09yL6MHc0RHaiojIpBXYiwiI3ETMxIjOw9GduMXdtNHauQnI6ISehxWZyJCLiYTMxEjM6A3b05yc112co5CdiojI0N3boJye"

# Flutter 版本
python3 build.py --flutter --hwcodec

# 直接构建
cargo build --release --features flutter,hwcodec
```

### iOS

```bash
# 设置环境变量
export RUSTDESK_CUSTOM_SERVER="==Qfi0zdHdlVBdWe4sCc4FHaiNlMqNkaQF1ZxgVMDZHOlZ3dBVVVJV0boNXYzgTNiojI5V2aiwiIyVmdyV2ctkGch1yazVGZ0NXdy9CcvRnLzVXbzhmL09yL6MHc0RHaiojIpBXYiwiI3ETMxIjOw9GduMXdtNHauQnI6ISehxWZyJCLiYTMxEjM6A3b05yc112co5CdiojI0N3boJye"

# 添加 iOS 目标
rustup target add aarch64-apple-ios

# 构建库
cargo build --features flutter,hwcodec --release --target aarch64-apple-ios --lib

# 构建 iOS 应用
cd flutter
flutter build ipa --release
```

## GitHub Actions 构建

### 1. 配置 GitHub Secrets

在您的 GitHub 仓库中：

1. 进入 **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret**
3. 添加以下 secret：
   - **Name**: `RUSTDESK_CUSTOM_SERVER`
   - **Secret**: 您的自定义服务器配置字符串

示例：
```
Name: RUSTDESK_CUSTOM_SERVER
Secret: ==Qfi0zdHdlVBdWe4sCc4FHaiNlMqNkaQF1ZxgVMDZHOlZ3dBVVVJV0boNXYzgTNiojI5V2aiwiIyVmdyV2ctkGch1yazVGZ0NXdy9CcvRnLzVXbzhmL09yL6MHc0RHaiojIpBXYiwiI3ETMxIjOw9GduMXdtNHauQnI6ISehxWZyJCLiYTMxEjM6A3b05yc112co5CdiojI0N3boJye
```

### 2. 触发构建

#### 方法 1: 手动触发（推荐）

1. 进入 **Actions** 标签页
2. 选择 **Build the flutter version of the RustDesk** 工作流
3. 点击 **Run workflow**
4. 选择分支（通常是 `master` 或 `main`）
5. 点击 **Run workflow** 按钮

#### 方法 2: 推送代码触发

如果工作流配置了 `push` 触发器，直接推送代码即可：

```bash
git add .
git commit -m "Build with custom server"
git push
```

#### 方法 3: 创建标签触发发布版

```bash
# 创建版本标签
git tag v1.4.5-custom
git push origin v1.4.5-custom
```

### 3. 下载构建产物

构建完成后：

1. 进入 **Actions** 标签页
2. 点击对应的工作流运行
3. 在 **Artifacts** 部分下载构建产物：
   - **Windows**: `rustdesk-<version>-windows-x86_64.zip`
   - **macOS**: `rustdesk-<version>-macos-x86_64.dmg` / `rustdesk-<version>-macos-aarch64.dmg`
   - **iOS**: `rustdesk-<version>.ipa`
   - **Linux**: `rustdesk-<version>-linux-x86_64.deb` / `.rpm` / `.AppImage`
   - **Android**: `rustdesk-<version>.apk`

### 4. 支持的平台

GitHub Actions 工作流支持以下平台的自动构建：

- ✅ **Windows** (x64, x86)
- ✅ **macOS** (x86_64, Apple Silicon)
- ✅ **iOS** (arm64)
- ✅ **Linux** (x64, arm64, armv7)
- ✅ **Android** (arm64-v8a, armeabi-v7a, x86_64)

## 验证构建

构建完成后，可以通过以下方式验证自定义服务器配置是否生效：

1. 运行程序
2. 查看日志输出，应该能看到：
   ```
   Using custom server config from build-time environment variable
   ```
3. 程序将自动连接到您配置的自定义服务器

## 注意事项

1. **环境变量优先级**：
   - 编译时环境变量 (RUSTDESK_CUSTOM_SERVER) - 最高优先级
   - Windows 可执行文件名中的配置
   - 运行时配置文件

2. **安全建议**：
   - 不要将服务器配置字符串提交到公开的代码仓库
   - 使用 GitHub Secrets 存储敏感配置
   - 定期更换服务器密钥

3. **构建时间**：
   - Windows 构建：约 30-45 分钟
   - macOS 构建：约 40-60 分钟
   - iOS 构建：约 35-50 分钟
   - Linux 构建：约 25-40 分钟
   - Android 构建：约 30-50 分钟

4. **存储空间**：
   - 确保 GitHub Actions 运行器有足够的磁盘空间
   - 每个平台的构建产物大小：50-150 MB

## 故障排查

### 构建失败

1. 检查 GitHub Secrets 是否正确设置
2. 查看 Actions 日志中的详细错误信息
3. 确认服务器配置字符串格式正确

### 运行时错误

如果仍然出现连接错误：

1. 检查自建服务器是否正常运行
2. 验证服务器地址和端口是否正确
3. 检查防火墙设置
4. 查看客户端和服务器日志

### 日志位置

- **Windows**: `%APPDATA%\RustDesk\logs\`
- **macOS**: `~/Library/Logs/RustDesk/`
- **Linux**: `~/.local/share/rustdesk/logs/`
- **iOS**: 通过 Xcode 查看设备日志

## 进阶配置

### 自定义工作流

您可以修改 `.github/workflows/flutter-build.yml` 来自定义构建流程：

```yaml
env:
  # 在这里添加更多环境变量
  RUSTDESK_CUSTOM_SERVER: "${{ secrets.RUSTDESK_CUSTOM_SERVER }}"
  # 例如：自定义版本号
  VERSION: "1.4.5-custom"
```

### 多服务器配置

如果需要为不同用户群体构建不同的客户端：

1. 创建多个 GitHub Secrets：
   - `RUSTDESK_CUSTOM_SERVER_PROD`
   - `RUSTDESK_CUSTOM_SERVER_TEST`

2. 创建不同的工作流文件或使用工作流输入参数

## 相关资源

- [RustDesk 官方文档](https://rustdesk.com/docs/)
- [自建服务器指南](https://rustdesk.com/docs/en/self-host/)
- [GitHub Actions 文档](https://docs.github.com/en/actions)

## 支持

如有问题，请提交 Issue 或查看：
- [RustDesk GitHub Issues](https://github.com/rustdesk/rustdesk/issues)
- [RustDesk 社区讨论](https://github.com/rustdesk/rustdesk/discussions)
