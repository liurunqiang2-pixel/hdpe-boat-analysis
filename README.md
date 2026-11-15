# HDPE 船舶设计工具工作台

这个仓库现在包含一个面向 HDPE 船舶设计的工程化原型，主要用于：

- 项目与版本管理
- HDPE 材料数据库
- 结构件和载荷工况管理
- FEA 分析任务定义
- 制造输出准备（BOM、焊缝清单、图纸导出）
- 审查和版本追溯

## 设计目标

将前面讨论的 CAD、结构分析、焊接制造和法规数据统一到一个工程工作台中，通过统一的项目数据模型连接船体设计、材料、分析和制造输出。

## 当前包含内容

- FastAPI 应用骨架
- SQLAlchemy 数据模型：项目、材料、结构件、工况、分析、制造包
- 示例 HDPE 材料数据
- API 路由：项目、材料、工况和分析
- 可扩展的服务层，方便接入 FreeCAD / Rhino / CalculiX / Abaqus / ANSYS

## 运行方式

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 说明

这个版本是工程原型，不替代成熟 CAD/FEA 软件。它的目标是把设计过程中的核心对象和工作流结构化，方便后续扩展到真实工程流程。

## 下一步扩展建议

1. 接入 FreeCAD 或 Rhino 参数化建模
2. 接入 CalculiX / Abaqus 生成和执行分析任务
3. 增加 DXF / STEP / BOM 导出模块
4. 增加审查流程和版本对比
5. 将材料数据从 JSON 扩展到完整数据库和可追溯来源记录
