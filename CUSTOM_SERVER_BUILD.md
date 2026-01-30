# 自定义服务器配置构建指南

## 修改说明

本次修改实现了在构建时将自定义服务器配置（ID服务器、中继服务器、API服务器、密钥）编译到应用程序中，支持所有平台（Windows、macOS、Linux、Android、iOS）。

## 修改的文件

### 0. 可复用脚本（便于维护）

**`.github/scripts/set_custom_server_config.py`**

- 从环境变量 `RUSTDESK_CUSTOM_SERVER` 读取导出的配置字符串
- 解码（反转 + Base64）后写入 `.cargo/config.toml` 的 `[env]` 段
- 各平台工作流统一调用此脚本，逻辑集中、便于维护
- 从仓库根目录执行：`python3 .github/scripts/set_custom_server_config.py`

### 1. 源代码修改（最小改动原则）

#### `src/common.rs`
- **修改位置 1**（第1031-1048行）：`get_custom_rendezvous_server` 函数
  - 添加了对编译时环境变量 `RENDEZVOUS_SERVER` 的支持
  - 当用户未配置自定义服务器时，使用编译时的默认值

- **修改位置 2**（第1525-1549行）：`get_key` 函数
  - 添加了对编译时环境变量 `KEY` 的支持
  - 当用户未配置密钥时，使用编译时的默认值

#### `src/rendezvous_mediator.rs`
- **修改位置**（第740-753行）：`get_relay_server` 函数
  - 添加了对编译时环境变量 `RELAY_SERVER` 的支持
  - 当服务器未提供中继服务器且用户未配置时，使用编译时的默认值

### 2. 构建工作流修改

#### `.github/workflows/flutter-build.yml`
为所有平台的构建任务添加了 "Set custom server config" 步骤，**统一调用** `.github/scripts/set_custom_server_config.py`：

1. **Windows Flutter 构建**：`python3 .github/scripts/set_custom_server_config.py`
2. **Windows Sciter 构建**：同上
3. **iOS 构建**：同上
4. **macOS 构建**：同上
5. **Android 构建**：同上
6. **Linux Flutter 构建**：在主机上执行脚本（写入工作区后再挂载进 Docker）
7. **Linux Sciter 构建**：在主机上执行脚本

脚本会：
- 从环境变量 `RUSTDESK_CUSTOM_SERVER` 读取配置字符串
- 解码配置（反转字符串 + Base64 解码）
- 将配置追加到 `.cargo/config.toml` 的 `[env]` 部分
- 设置以下编译时环境变量：`RENDEZVOUS_SERVER`、`RELAY_SERVER`、`API_SERVER`、`KEY`

## 使用方法

### 1. 导出配置

在原始 RustDesk 客户端中：
1. 进入设置 → 网络 → ID/中继服务器
2. 填写你的服务器配置
3. 点击"导出服务器配置"按钮
4. 配置会被复制到剪贴板（已加密）

### 2. 设置 GitHub Secret

1. 进入你的 GitHub 仓库
2. 设置 → Secrets and variables → Actions
3. 创建新的 Repository Secret：
   - Name: `RUSTDESK_CUSTOM_SERVER`
   - Value: 粘贴从客户端导出的加密配置字符串

### 3. 触发构建

运行 GitHub Actions 工作流 "Build the flutter version of the RustDesk"，构建出的应用程序将包含你的默认服务器配置。

## 配置格式说明

导出的配置是一个 JSON 对象，经过以下处理：
1. JSON 字符串 → UTF-8 字节
2. Base64 URL 编码
3. 字符串反转

解码过程：
```python
import json
import base64

config_str = "你的加密配置字符串"
reversed_str = config_str[::-1]
decoded_bytes = base64.b64decode(reversed_str)
config = json.loads(decoded_bytes.decode('utf-8'))

# config 包含:
# {
#   "host": "ID服务器地址",
#   "relay": "中继服务器地址", 
#   "api": "API服务器地址",
#   "key": "服务器公钥"
# }
```

## 工作原理

1. **编译时注入**：通过 Cargo 的 `[env]` 配置，将服务器信息作为编译时环境变量传递给 Rust 编译器

2. **代码读取**：Rust 代码使用 `option_env!()` 宏读取这些编译时环境变量

3. **优先级**：
   - 最高优先级：用户在应用中手动配置的服务器
   - 中等优先级：编译时默认配置（本次修改添加）
   - 最低优先级：硬编码的公共服务器地址

4. **用户体验**：
   - 首次启动应用时，服务器配置已经填好
   - 用户仍然可以在设置中修改服务器配置
   - 修改后的配置会保存在本地，优先级高于编译时默认值

## 验证方法

构建完成后，安装应用程序：
1. 首次启动应用
2. 进入设置 → 网络 → ID/中继服务器
3. 检查服务器地址是否已经填写为你的自定义配置

## 注意事项

1. **安全性**：虽然配置经过 Base64 编码和字符串反转，但这不是加密，只是编码。不要在配置中包含敏感信息（如密码）。

2. **密钥格式**：`KEY` 字段应该是服务器的公钥（Base64 编码），用于验证服务器身份。

3. **兼容性**：此修改完全向后兼容，不影响现有的配置方式。

4. **构建缓存**：修改配置后需要清除 Rust 构建缓存，否则可能使用旧的编译结果。GitHub Actions 会自动处理这个问题。

## 技术细节

### 环境变量传递路径

```
GitHub Secret (RUSTDESK_CUSTOM_SERVER)
  ↓
GitHub Actions 环境变量
  ↓
Python 脚本解码
  ↓
.cargo/config.toml [env] 部分
  ↓
Cargo 编译时环境变量
  ↓
Rust option_env!() 宏
  ↓
应用程序默认配置
```

### 修改的编译时环境变量

| 环境变量 | 对应配置项 | 使用位置 |
|---------|-----------|---------|
| `RENDEZVOUS_SERVER` | ID服务器 | `src/common.rs::get_custom_rendezvous_server()` |
| `RELAY_SERVER` | 中继服务器 | `src/rendezvous_mediator.rs::get_relay_server()` |
| `API_SERVER` | API服务器 | `src/common.rs::get_api_server_()` |
| `KEY` | 服务器公钥 | `src/common.rs::get_key()` |

## 故障排除

### 问题：构建后配置未生效

**可能原因**：
1. GitHub Secret 未正确设置
2. 配置字符串格式错误
3. Rust 构建缓存未清除

**解决方法**：
1. 检查 GitHub Actions 日志中的 "Set custom server config" 步骤
2. 确认是否输出了 "✓ 已设置自定义服务器配置"
3. 如果输出 "✗ 解析配置失败"，检查配置字符串是否正确

### 问题：某个平台的配置未生效

**可能原因**：该平台的构建步骤未添加配置步骤

**解决方法**：检查 `.github/workflows/flutter-build.yml` 中对应平台是否有 "Set custom server config" 步骤

## 贡献

如有问题或改进建议，请提交 Issue 或 Pull Request。
