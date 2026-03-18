# CryChiC 架构设计 v0.1

## 项目定位
CryChiC 是一个面向中文母语者的 ACG 日语词典/语感学习系统。

目标不是做 anime 原文台词数据库，而是：
- 基于正规词典和例句数据构建事实底座
- 利用 LLM 离线生成中文解释、语境说明、近义词差异和 ACG 风格原创例句
- 通过审计环节控制幻觉、风格漂移和版权风险

## 核心原则
1. LLM 用于离线内容生产，不直接暴露给终端用户。
2. 每个 job 独立运行，尽量不依赖长上下文。
3. 所有状态保存在文件、manifest 和数据库中，而不是会话上下文。
4. provider 可替换，stage 不直接绑定具体模型供应商。

## 核心抽象
采用三层解耦：

```text
stage -> profile -> provider
```

- `stage`：业务阶段，例如 `sense_explainer`、`example_generator`、`auditor`
- `profile`：能力/成本策略，例如 `cheap_gen`、`balanced_explain`、`strong_audit`
- `provider`：真实模型入口，例如 `anthropic_direct`、`litellm_gateway`、`claude_code_headless`

## 设计理由
这样做的好处：
- 换 provider 不改业务逻辑
- 不同 stage 可按成本/质量选不同模型
- provider 挂掉时可 fallback
- Claude Code 可以作为 premium worker，而不是唯一入口

## Pipeline 结构
推荐 nightly pipeline：

1. `sense_explainer`
   - 生成中文母语者友好的词义解释
   - 写出 reality vs ACG 差异
   - 输出 misuse_warning

2. `example_generator`
   - 生成现实常用句
   - 生成 ACG 风格原创教学例句

3. `contrast_writer`
   - 生成近义词/易混词差异说明

4. `tag_infer`
   - 推断场景、语气、角色感标签

5. `auditor`
   - 独立审计词义、语感、自然度、版权风险、标签一致性

6. `repair`
   - 对不通过的内容做局部修复

## Provider 切换实现思路
### 官方能力
1. Claude Code Headless / Print Mode
   - 用作非交互式 worker
   - 适合高质量审计和少量 premium 重写

2. Claude Code Gateway / Base URL 接法
   - 允许 Claude Code 接入自定义 gateway / proxy
   - 为 provider 兼容层提供入口

3. settings / env
   - 用于本地调试和临时 override

4. resume
   - 只用于故障恢复，不作为主流程

### 社区能力
1. LiteLLM
   - 作为统一 gateway / router
   - 提供 routing、fallback、load balancing 思路

2. ccrelay / claude-code-proxy / provider-proxy
   - 用于 Anthropic 风格请求到 OpenAI-compatible provider 的兼容转换
   - 支持 model mapping 和代理切换

3. cc-switch / claude-code-switch
   - 用于本地人工调试与手动切换
   - 不作为 nightly pipeline 主控制层

## 推荐实现分工
- 你自己的代码：
  - orchestrator
  - stage/profile/provider 抽象
  - manifest/checkpoint/retry
  - JSON schema 校验
- Claude Code：
  - premium worker
  - 高质量审计和重写
- LiteLLM / proxy：
  - 路由层
  - provider fallback

## 目录建议
```text
configs/
  providers.yaml
  profiles.yaml
  stages.yaml
  taxonomy.yaml
  style_guide.md

prompts/
  sense_explainer.md
  example_generator.md
  contrast_writer.md
  tag_infer.md
  auditor.md
  repair.md

schemas/
  sense.schema.json
  examples.schema.json
  audit.schema.json

scripts/
  run_stage.py
```

## 第一版落地建议
- 事实底座：JMdict + Tatoeba + Wiktionary/Kaikki 补充
- 批处理框架：Python + while loop + manifest
- provider 层：LiteLLM 风格统一接口
- premium worker：Claude Code headless
- 内容范围：先做 50~100 个高价值 ACG 词条
