# GitHub Actions 自动构建发行版指南

## 快速开始

### 1. 配置自定义服务器 Secret

1. 打开您的 GitHub 仓库
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**
4. 填写：
   ```
   Name: RUSTDESK_CUSTOM_SERVER
   Secret: ==Qfi0zdHdlVBdWe4sCc4FHaiNlMqNkaQF1ZxgVMDZHOlZ3dBVVVJV0boNXYzgTNiojI5V2aiwiIyVmdyV2ctkGch1yazVGZ0NXdy9CcvRnLzVXbzhmL09yL6MHc0RHaiojIpBXYiwiI3ETMxIjOw9GduMXdtNHauQnI6ISehxWZyJCLiYTMxEjM6A3b05yc112co5CdiojI0N3boJye
   ```
   （替换为您自己的服务器配置字符串）

### 2. 触发构建

**方法 A - 手动触发（推荐）：**

1. 进入 **Actions** 标签页
2. 选择 **Build the flutter version of the RustDesk**
3. 点击右侧 **Run workflow**
4. 选择分支（如 `master`）
5. 点击绿色的 **Run workflow** 按钮

**方法 B - 推送代码触发：**

```bash
git commit -m "触发构建"
git push
```

**方法 C - 创建发布标签：**

```bash
git tag v1.4.5-custom
git push origin v1.4.5-custom
```

### 3. 下载构建产物

1. 在 **Actions** 标签页找到您的工作流运行
2. 等待构建完成（绿色勾号✅）
3. 滚动到页面底部 **Artifacts** 部分
4. 下载对应平台的安装包：

| 平台 | 文件名示例 | 大小 |
|------|-----------|------|
| Windows x64 | `rustdesk-1.4.5-windows-x86_64.zip` | ~80 MB |
| Windows x86 | `rustdesk-1.4.5-windows-x86.zip` | ~70 MB |
| macOS Intel | `rustdesk-1.4.5-macos-x86_64.dmg` | ~90 MB |
| macOS Apple Silicon | `rustdesk-1.4.5-macos-aarch64.dmg` | ~85 MB |
| iOS | `rustdesk-1.4.5.ipa` | ~60 MB |
| Linux x64 | `rustdesk-1.4.5-linux-x86_64.deb` | ~70 MB |
| Android | `rustdesk-1.4.5.apk` | ~50 MB |

## 构建时间参考

| 平台 | 预计时间 |
|------|----------|
| Windows | 30-45 分钟 |
| macOS | 40-60 分钟 |
| iOS | 35-50 分钟 |
| Linux | 25-40 分钟 |
| Android | 30-50 分钟 |

## 签名配置（可选）

如果需要签名发布版，需要额外配置以下 Secrets：

### Windows 签名

```
WINDOWS_SIGN_CERTIFICATE  # PFX 证书 Base64
WINDOWS_SIGN_PASSWORD     # 证书密码
```

### macOS 签名

```
MACOS_P12_BASE64          # .p12 证书 Base64
MACOS_P12_PASSWORD        # 证书密码
MACOS_DEVELOPER_ID        # Apple Developer ID
```

### iOS 签名

```
IOS_CERTIFICATE_BASE64    # 分发证书 Base64
IOS_PROVISION_PROFILE     # Provisioning Profile Base64
IOS_CERTIFICATE_PASSWORD  # 证书密码
```

### Android 签名

```
ANDROID_SIGNING_KEY       # Keystore Base64
ANDROID_KEY_ALIAS         # Key 别名
ANDROID_KEY_PASSWORD      # Key 密码
ANDROID_STORE_PASSWORD    # Keystore 密码
```

## 高级配置

### 自定义版本号

修改 `.github/workflows/flutter-build.yml`：

```yaml
env:
  VERSION: "1.4.5"  # 修改这里
```

### 仅构建特定平台

在工作流文件中注释掉不需要的 job：

```yaml
jobs:
  # build-for-windows-flutter:  # 注释掉不构建 Windows
  build-for-macos-flutter:      # 只构建 macOS
  # build-for-linux-flutter:    # 注释掉不构建 Linux
```

## 验证构建结果

### 1. 检查构建日志

在构建过程中应该看到：

```
cargo:warning=Building with custom server config
```

### 2. 运行程序验证

启动构建的客户端，查看日志文件，应该包含：

```
Using custom server config from build-time environment variable
```

### 3. 测试连接

尝试连接到远程设备，确认使用的是您的自建服务器。

## 常见问题

### Q1: 构建失败，提示 "Secret not found"

**A:** 确保在仓库的 Settings → Secrets 中正确添加了 `RUSTDESK_CUSTOM_SERVER`

### Q2: 构建成功但程序不使用自定义服务器

**A:** 检查：
1. Secret 的值是否正确
2. 构建日志中是否有 "Building with custom server config" 提示
3. 是否下载了正确的构建产物

### Q3: iOS 构建失败

**A:** iOS 构建需要 macOS runner，确保：
1. 使用的是 `macos-latest` 或 `macos-13` runner
2. 已安装 Xcode 和 Flutter

### Q4: 构建时间过长

**A:** 
- 首次构建会下载依赖，耗时较长
- 后续构建会使用缓存，速度较快
- 可以只构建需要的平台以节省时间

### Q5: 如何查看详细日志

**A:** 点击 Actions → 选择运行 → 点击具体的 job → 展开每个步骤查看详细输出

## 修改内容说明

此版本修复了以下问题：

1. **核心修复** (`src/ui_session_interface.rs:1927`)
   - 移除了错误使用的 `access_token`
   - 修复了使用自建服务器时 "deadline has elapsed" 超时错误

2. **构建增强** (`build.rs`)
   - 支持从环境变量 `RUSTDESK_CUSTOM_SERVER` 读取服务器配置
   - 编译时嵌入配置，无需修改可执行文件名

3. **Windows 平台优化** (`src/platform/windows.rs`)
   - 优先使用编译时嵌入的服务器配置
   - 保持向后兼容可执行文件名配置方式

4. **CI/CD 集成** (`.github/workflows/flutter-build.yml`)
   - 自动从 GitHub Secrets 读取服务器配置
   - 所有平台构建统一使用自定义服务器

## 技术支持

遇到问题？

1. 查看 [完整构建文档](./CUSTOM_SERVER_BUILD.md)
2. 提交 [GitHub Issue](https://github.com/rustdesk/rustdesk/issues)
3. 参与 [社区讨论](https://github.com/rustdesk/rustdesk/discussions)

## 文件清单

构建修改涉及的文件：

```
src/ui_session_interface.rs          # 核心修复
build.rs                              # 构建脚本
src/platform/windows.rs               # Windows 平台支持
.github/workflows/flutter-build.yml   # CI/CD 配置
CUSTOM_SERVER_BUILD.md                # 完整文档
GITHUB_ACTIONS_构建说明.md            # 本文档
```

---

**提示**: 首次构建建议先使用手动触发方式，确认配置正确后再设置自动触发。
