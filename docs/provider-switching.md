# Provider Switching 设计说明 v0.1

## 目标
CryChiC 需要支持在离线内容生产流水线中频繁切换模型供应商，以便根据成本、质量、稳定性和可用性做动态取舍。

目标不是单纯“切 Claude Code 的默认配置”，而是让整个 nightly pipeline 在业务层不感知底层 provider 差异。

## 设计原则
1. stage 不直接绑定具体 provider
2. provider 切换由 profile 和 provider_chain 驱动
3. Claude Code 是 premium worker，不是唯一执行入口
4. provider 挂掉时允许 fallback
5. 所有切换逻辑可配置、可审计、可回放

## 三层抽象
```text
stage -> profile -> provider
```

### stage
表示业务阶段，例如：
- sense_explainer
- example_generator
- auditor

### profile
表示能力/成本策略，例如：
- cheap_gen
- balanced_explain
- strong_audit

### provider
表示真实执行入口，例如：
- anthropic_direct
- litellm_gateway
- claude_code_headless

## 切换机制
### 1. stage 选择 profile
例如：
- example_generator -> cheap_gen
- auditor -> strong_audit

### 2. profile 定义 provider_chain
例如：
- cheap_gen: litellm_gateway -> glm_direct -> openrouter_direct
- strong_audit: anthropic_direct -> claude_code_headless

### 3. 执行器顺序尝试 provider
- 成功：直接返回结果
- 失败：记录 manifest 并 fallback
- 全部失败：标记该 stage 失败

## 官方能力怎么用
### Claude Code Headless / Print Mode
用途：
- 非交互式 worker
- 高质量审计
- premium 重写

### Claude Code Gateway / Base URL
用途：
- 让 Claude Code 接到自定义 gateway / proxy
- 背后实际 provider 可替换

### settings / env
用途：
- 本地调试
- 手工 override
- 项目级切换

### resume
用途：
- 单 job 故障恢复
- 不作为主流程

## 社区能力怎么用
### LiteLLM
用途：
- 统一 gateway / router
- 支持 routing、fallback、统一接口
- 适合批量 stage 的程序化执行

### ccrelay / claude-code-proxy / provider-proxy
用途：
- Anthropic 请求到 OpenAI-compatible provider 的兼容转换
- 模型映射
- 让 Claude Code 背后可切 provider

### cc-switch / claude-code-switch
用途：
- 本地人工调试和手动切换
- 不作为生产 pipeline 主控制层

## 推荐落地
### 批量生成类 stage
优先：LiteLLM gateway
- example_generator
- tag_infer

### 高质量审计类 stage
优先：Anthropic direct / Claude Code headless
- auditor
- premium_rewrite

### 本地手工调试
优先：cc-switch / settings / env

## 最终建议
- 主路由层：LiteLLM 风格统一入口
- premium worker：Claude Code headless
- 手工调试层：cc-switch 类工具
- 编排层：你自己的 Python orchestrator
