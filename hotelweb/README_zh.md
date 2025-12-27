# 酒店集团平台 (Hotel Group Platform)

这是一个基于 Flask 开发的高端酒店预订 Web 应用。它模仿了 IHG/Marriott 等大型酒店集团的体验，具备实时房型库存搜索、设施筛选、用户预订管理等核心功能，并采用了现代化的响应式设计。

## 核心功能

- **用户认证系统**：支持用户注册、登录、登出，使用安全的密码哈希存储。
- **智能可订房搜索**：
    - **日期重叠算法**：核心算法能够精确计算指定日期区间内的已占用库存，只返回真正可用的房型。
    - **设施筛选**：支持按城市、人数、房间数以及具体设施（如 WiFi、泳池等）进行严格筛选。
- **预订管理**：登录用户可以创建预订，并在个人中心查看或取消自己的预订（库存会自动释放）。
- **多对多关系展示**：房型与设施（Amenity）之间建立多对多数据库关联，用于前端的高级筛选和匹配度展示。
- **高级 UI/UX**：
    - 响应式布局，完美适配手机、平板和桌面。
    - 符合 WCAG 无障碍标准（清晰的焦点、对比度、ARIA 标签）。
    - 独立且专业的 CSS/JS 静态文件结构。

## 技术栈

- **后端**：Python, Flask (Blueprints), SQLAlchemy (ORM), Werkzeug (Security)
- **数据库**：开发环境使用 SQLite，生产环境支持配置 `DATABASE_URL` (如 MySQL)。
- **前端**：Jinja2 模板引擎, HTML5, Vanilla CSS3 (自定义高级样式), JavaScript (ES6+), Bootstrap 5 (仅用于网格系统)。

## 安装与运行

### 1. 环境准备

确保您的系统已安装 Python 3.8 或更高版本。

```bash
# 克隆代码库 (如果您还没下载)
git clone <repository-url>
cd hotelweb
```

### 2. 安装依赖

建议创建虚拟环境：

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

安装所需 Python 包：

```bash
pip install -r requirements.txt
```

### 3. 初始化数据库与数据填充

即使是第一次运行，我们也提供了一键脚本来初始化数据库表格，并自动填充测试数据（城市、酒店、房型、设施等）：

```bash
python scripts/seed_data.py
```
*运行成功后会显示 "Database seeded successfully!"*

### 4. 启动应用

最简单的方式是直接运行根目录下的 `run.py`：

```bash
python run.py
```

或者使用 Flask 命令行：

```bash
# Mac/Linux
export FLASK_APP=hotelweb
flask run

# Windows (PowerShell)
$env:FLASK_APP = "hotelweb"
flask run
```

然后打开浏览器访问：`http://127.0.0.1:5000`

### 5. 测试账号

系统预置了一个测试用户：
- **邮箱**：`test@example.com`
- **密码**：`password`

当然，您也可以在注册页面注册新账号。

## 项目结构概览

```
hotelweb/
├── app.py              # 应用入口与工厂函数
├── config.py           # 配置管理 (支持环境变量)
├── extensions.py       # 第三方扩展初始化 (DB, LoginManager)
├── models.py           # 数据库模型定义
├── auth/               # 用户认证模块 (Blueprint)
├── main/               # 核心业务模块 (搜索/预订 Blueprint)
│   ├── routes.py       # 路由逻辑
│   └── services.py     # 核心搜索算法实现
├── scripts/
│   └── seed_data.py    # 数据填充脚本
├── static/             # 静态资源
│   ├── css/main.css    # 自定义样式
│   └── js/main.js      # 前端交互脚本
└── templates/          # 页面模板
```

## 部署 (PythonAnywhere)

本项目已为部署做好准备：
1. 将代码上传至 PythonAnywhere。
2. 配置虚拟环境并安装依赖。
3. 如果需要使用 MySQL，请在 Web 面板配置 `DATABASE_URL` 环境变量；否则默认使用 SQLite。
4. 将 WSGI 配置文件指向 `create_app()`。
5. 在 Web 选项卡中配置静态文件路径映射 (`/static/` -> 你的项目 `static` 目录)。
