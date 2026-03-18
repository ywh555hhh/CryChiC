# CryChiC

一个面向中文母语者的 ACG 日语词典/内容工厂项目。

## 当前保存内容
- 架构设计文档
- provider/profile/stage 配置草案
- 内容生产风格指南
- JSON Schema 草案
- `run_stage.py` pipeline skeleton

## 当前核心方向
- LLM 用于离线内容生产与审计，不直接暴露给终端用户
- 使用 nightly batch pipeline 跑批生成词典内容
- 采用 `stage -> profile -> provider` 的解耦架构
- 支持频繁切换 provider，以平衡成本与质量

## 目录说明
- `docs/`：架构与设计文档
- `configs/`：pipeline 配置草案
- `schemas/`：结构化输出 schema
- `scripts/`：pipeline skeleton
