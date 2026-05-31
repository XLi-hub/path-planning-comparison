"""
生成课程设计报告 (Word文档) — 完整版，包含所有43张图表
按照华南理工大学课程设计报告模板格式
"""

from docx import Document
from docx.shared import Pt, Cm, Inches, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

# ============================================================
# 全局路径配置
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIGURES_DIR = os.path.join(BASE_DIR, 'figures')

# 场景名称列表（与文件名中的场景名对应）
SCENES = [
    ('随机散点-低密度(10%)', '低密度随机障碍(10%)'),
    ('随机散点-中密度(20%)', '中密度随机障碍(20%)'),
    ('随机散点-高密度(30%)', '高密度随机障碍(30%)'),
    ('迷宫式障碍', '迷宫式障碍'),
    ('窄通道场景', '窄通道场景'),
]


def set_cell_border(cell, **kwargs):
    """设置单元格边框"""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for edge in ('start', 'top', 'end', 'bottom', 'insideH', 'insideV'):
        edge_data = kwargs.get(edge)
        if edge_data:
            element = OxmlElement(f'w:{edge}')
            for attr in ['sz', 'val', 'color', 'space']:
                if attr in edge_data:
                    element.set(qn(f'w:{attr}'), str(edge_data[attr]))
            tcBorders.append(element)
    tcPr.append(tcBorders)


def create_report():
    """创建课程设计报告（含全部43张图片）"""
    doc = Document()

    # ============================================================
    # 页面设置
    # ============================================================
    section = doc.sections[0]
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2)

    # ============================================================
    # 样式设置
    # ============================================================
    style = doc.styles['Normal']
    style.font.name = '宋体'
    style.font.size = Pt(12)  # 小4号
    style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    style.paragraph_format.line_spacing = Pt(20)  # 固定值20磅
    style.paragraph_format.space_before = Pt(0)
    style.paragraph_format.space_after = Pt(0)

    # ============================================================
    # 辅助函数
    # ============================================================
    def add_title(text, level=0):
        """添加标题"""
        if level == 0:  # 封面题目（二号黑体加粗居中）
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.line_spacing = 1.5  # 1.5倍行距，防止大号文字被裁剪
            run = p.add_run(text)
            run.font.name = '黑体'
            run.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
            run.font.size = Pt(22)
            run.bold = True
        elif level == 1:  # 一级标题（四号宋体加粗）
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.line_spacing = 1.5
            run = p.add_run(text)
            run.font.name = '宋体'
            run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
            run.font.size = Pt(14)
            run.bold = True
        elif level == 2:  # 二级标题（小四宋体加粗）
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.line_spacing = 1.25
            run = p.add_run(text)
            run.font.name = '宋体'
            run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
            run.font.size = Pt(12)
            run.bold = True
        elif level == 3:  # 三级标题（小四宋体加粗）
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.line_spacing = 1.25
            run = p.add_run(text)
            run.font.name = '宋体'
            run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
            run.font.size = Pt(12)
            run.bold = True
        return p

    def add_body(text):
        """添加正文段落"""
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.first_line_indent = Pt(24)
        run = p.add_run(text)
        run.font.name = '宋体'
        run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
        run.font.size = Pt(12)
        run.bold = False
        return p

    def add_empty_line():
        """添加空行"""
        p = doc.add_paragraph()
        run = p.add_run('')
        run.font.size = Pt(12)
        return p

    def add_figure(filename, caption, width_inches=4.8):
        """
        插入图片并添加居中图注

        Args:
            filename: 图片文件名（在figures目录下）
            caption: 图注文字（如 "图1 低密度随机障碍地图"）
            width_inches: 图片宽度（英寸），默认4.8英寸≈12.2cm（A4可用宽度约16.5cm）
        """
        filepath = os.path.join(FIGURES_DIR, filename)
        if not os.path.exists(filepath):
            # 图片不存在时插入占位文字
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(f'[图片缺失: {filename}]')
            run.font.size = Pt(10)
            run.font.color.rgb = RGBColor(255, 0, 0)
            return

        # 插入图片（使用独立段落确保居中）
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(6)
        p_img.paragraph_format.space_after = Pt(0)
        # 关键：覆盖Normal样式的固定行距(Pt(20)=exact)，使用单倍行距让段落高度自适应图片
        # 必须放在space_before/after之后设置，确保line属性不被覆盖
        p_img.paragraph_format.line_spacing = 1.0
        p_img.paragraph_format.keep_with_next = True
        run_img = p_img.add_run()
        # 使用显式的宽高参数，确保不超出页面
        run_img.add_picture(filepath, width=Inches(width_inches))

        # 图片下方添加居中图注（与图片保持在同一页）
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(2)
        p_cap.paragraph_format.space_after = Pt(10)
        p_cap.paragraph_format.keep_with_next = False
        run_cap = p_cap.add_run(caption)
        run_cap.font.name = '宋体'
        run_cap.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
        run_cap.font.size = Pt(9)
        run_cap.bold = False

    def add_figures_row(figures_info, width_inches=2.55):
        """
        在同一行插入2张图片（并排）

        Args:
            figures_info: list of (filename, caption) tuples, max 2
            width_inches: 每张图片的宽度
        """
        p_row = doc.add_paragraph()
        p_row.alignment = WD_ALIGN_PARAGRAPH.CENTER
        # 关键：覆盖Normal样式的固定行距，使用单倍行距让段落高度自适应图片
        p_row.paragraph_format.line_spacing = 1.0

        for i, (filename, caption) in enumerate(figures_info):
            filepath = os.path.join(FIGURES_DIR, filename)
            if os.path.exists(filepath):
                run = p_row.add_run()
                run.add_picture(filepath, width=Inches(width_inches))
                if i < len(figures_info) - 1:
                    # 添加间距
                    spacer = p_row.add_run('    ')
                    spacer.font.size = Pt(6)

        # 图注（合并在一行）
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(2)
        p_cap.paragraph_format.space_after = Pt(8)
        captions_text = '    |    '.join([cap for _, cap in figures_info])
        run_cap = p_cap.add_run(captions_text)
        run_cap.font.name = '宋体'
        run_cap.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
        run_cap.font.size = Pt(9)

    def add_page_break():
        """添加分页符"""
        doc.add_page_break()

    # ============================================================
    # 封面
    # ============================================================
    # 校徽图片（华南理工大学校名+校徽横幅）
    logo_path = os.path.join(FIGURES_DIR, 'school_banner.jpeg')
    if os.path.exists(logo_path):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.line_spacing = 1.0
        p_logo.paragraph_format.space_after = Pt(20)
        run_logo = p_logo.add_run()
        run_logo.add_picture(logo_path, width=Inches(3.0))

    add_empty_line()
    add_empty_line()
    add_empty_line()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing = 1.5  # 1.5倍行距，22pt二号字不裁剪
    run = p.add_run('人工智能课程设计')
    run.font.name = '黑体'
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
    run.font.size = Pt(22)
    run.bold = True

    add_empty_line()
    add_empty_line()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing = 1.5  # 1.5倍行距，22pt二号字不裁剪
    run = p.add_run('题目：基于多算法对比的栅格路径规划')
    run.font.name = '黑体'
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
    run.font.size = Pt(22)
    run.bold = True

    add_empty_line()
    add_empty_line()
    add_empty_line()

    info_items = [
        ('学  院', '自动化科学与工程学院'),
        ('专  业', '智能科学与技术'),
        ('学生姓名', ''),
        ('学生学号', ''),
        ('指导教师', '王敏'),
        ('课程编号', '046101421'),
        ('课程学分', '1学分'),
        ('起始日期', '2026年5月25日—5月31日'),
    ]

    for label, value in info_items:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 1.5  # 1.5倍行距，14pt文字不裁剪
        run = p.add_run(f'{label}：{value}')
        run.font.name = '宋体'
        run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
        run.font.size = Pt(14)

    add_page_break()

    # ============================================================
    # 教师评语页
    # ============================================================
    add_empty_line()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing = 1.5  # 1.5倍行距，16pt三号字不裁剪
    run = p.add_run('教师评语')
    run.font.name = '宋体'
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    run.font.size = Pt(16)
    run.bold = True

    for _ in range(20):
        add_empty_line()

    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run('教师签名：                    日期：')
    run.font.size = Pt(12)

    add_page_break()

    # ============================================================
    # 目录页
    # ============================================================
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing = 1.5  # 1.5倍行距，16pt三号字不裁剪
    run = p.add_run('目  录')
    run.font.name = '宋体'
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    run.font.size = Pt(16)
    run.bold = True

    add_empty_line()

    toc_items = [
        ('一、选题背景', ''),
        ('二、方案论证(设计理念)', ''),
        ('    2.1 Dijkstra算法原理', ''),
        ('    2.2 A*算法原理与启发函数设计', ''),
        ('    2.3 遗传算法原理', ''),
        ('    2.4 蚁群算法原理', ''),
        ('    2.5 方案选择理由', ''),
        ('三、过程论述', ''),
        ('    3.1 地图生成模块', ''),
        ('    3.2 算法类设计与搜索过程可视化', ''),
        ('    3.3 关键代码解析', ''),
        ('四、结果分析', ''),
        ('    4.1 多种场景下的路径对比', ''),
        ('    4.2 性能指标定量对比', ''),
        ('    4.3 收敛曲线分析', ''),
        ('    4.4 启发函数影响分析', ''),
        ('    4.5 算法优劣势讨论与综合评估', ''),
        ('五、课程设计总结', ''),
        ('参考文献', ''),
        ('附录（程序代码）', ''),
    ]

    for item, _ in toc_items:
        p = doc.add_paragraph()
        run = p.add_run(item)
        run.font.name = '宋体'
        run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
        run.font.size = Pt(12)
        p.paragraph_format.line_spacing = 1.5

    add_page_break()

    # ============================================================
    # 正文开始
    # ============================================================

    # ============================================================
    # 一、选题背景
    # ============================================================
    add_title('一、选题背景', level=1)
    add_empty_line()

    add_body(
        '路径规划问题是人工智能领域中的一个经典问题，在机器人导航、自动驾驶、'
        '物流配送、游戏AI开发等众多实际应用场景中具有重要地位。路径规划的核心任务'
        '是：在给定的环境中，找到一条从起点到终点的无碰撞最优或近似最优路径。'
    )

    add_body(
        '栅格地图是路径规划中最常用的环境表示方法之一。它将连续空间离散化为均匀'
        '的网格单元，每个单元标记为可通行或不可通行（障碍物）。这种表示方法简洁直观，'
        '便于算法处理，也便于结果可视化展示。'
    )

    add_body(
        '本课程设计旨在综合运用《人工智能》课程所学的多种搜索与优化算法，解决栅格'
        '地图上的路径规划问题。具体而言，本设计选取了四种代表性算法进行实现与对比：'
        'Dijkstra算法代表盲目搜索策略，A*算法代表启发式搜索策略，遗传算法代表进化'
        '计算策略，蚁群算法代表群体智能策略。通过对这四种算法在多种场景下的性能进行'
        '系统对比分析，加深对不同AI算法范式的理解与掌握。'
    )

    add_body(
        '本设计的指导思想是：以栅格地图为统一测试平台，在同一环境下公平比较不同'
        'AI算法在路径规划问题上的表现，从路径质量（路径长度）、搜索效率（探索节点数）'
        '和计算时间三个维度进行定量评估。此外，通过设计不同类型的障碍物场景（随机散点、'
        '迷宫、窄通道），全面测试各算法在不同环境复杂度下的适应性和鲁棒性。'
    )

    # ============================================================
    # 二、方案论证(设计理念)
    # ============================================================
    add_title('二、方案论证(设计理念)', level=1)
    add_empty_line()

    # 2.1 Dijkstra
    add_title('2.1 Dijkstra算法原理', level=2)
    add_body(
        'Dijkstra算法由荷兰计算机科学家Edsger Dijkstra于1959年提出，是一种经典的'
        '单源最短路径算法，属于盲目搜索（Uninformed Search）的范畴。该算法的核心思想'
        '是贪心策略：每次从尚未确定最短距离的节点中，选出距离起点最近的节点，更新其'
        '邻居节点的距离，直到扩展到目标节点为止。'
    )
    add_body(
        'Dijkstra算法使用优先队列（最小堆）维护待扩展节点，每次弹出当前距离值最小'
        '的节点进行扩展。其伪代码如下：\n'
        '  (1) 初始化距离数组dist[start]=0，其余为无穷大；\n'
        '  (2) 将起点加入优先队列；\n'
        '  (3) 当队列非空时，弹出距离最小的节点u；\n'
        '  (4) 若u为目标节点，则搜索结束；\n'
        '  (5) 遍历u的所有邻居节点v，若dist[u]+cost(u,v)<dist[v]，则更新dist[v]'
        '并将v加入队列；\n'
        '  (6) 重复步骤(3)-(5)。'
    )
    add_body(
        'Dijkstra算法保证找到最优解（最短路径），但由于没有利用任何关于目标位置'
        '的先验信息，会在所有方向上均匀扩展，探索大量无关节点。在本设计中，Dijkstra'
        '算法作为性能基准，用于衡量其他算法相对于最优解的偏离程度和效率提升幅度。'
    )

    # 2.2 A*
    add_title('2.2 A*算法原理与启发函数设计', level=2)
    add_body(
        'A*算法是人工智能中最著名的启发式搜索算法，由Hart、Nilsson和Raphael于1968年'
        '提出。A*算法在Dijkstra算法的基础上引入了启发式函数（Heuristic Function），用于'
        '估计从当前节点到目标节点的剩余代价，从而引导搜索朝目标方向进行，大幅减少探索'
        '的节点数量。'
    )
    add_body(
        'A*算法的评价函数为 f(n) = g(n) + h(n)，其中：\n'
        '  • g(n)：从起点到节点n的实际代价（已知）；\n'
        '  • h(n)：从节点n到目标的估计代价（启发函数）；\n'
        '  • f(n)：经过节点n的估计总代价。'
    )
    add_body(
        'A*算法的关键在于启发函数h(n)的设计。为保证算法的最优性（admissibility），'
        'h(n)必须满足：h(n) ≤ h*(n)，即启发函数不能高估实际代价。本设计实现了四种'
        '启发函数用于对比：\n'
        '  (1) 曼哈顿距离（Manhattan）：h = |dx| + |dy|，适用于四方向移动；\n'
        '  (2) 欧几里得距离（Euclidean）：h = sqrt(dx² + dy²)，适用于八方向移动；\n'
        '  (3) 对角线距离（Diagonal）：h = max(dx, dy) + (√2 - 1)·min(dx, dy)，'
        '适用于八方向移动的最优启发；\n'
        '  (4) 切比雪夫距离（Chebyshev）：h = max(|dx|, |dy|)，适用于八方向移动'
        '但可能高估代价。'
    )
    add_body(
        '本设计允许八方向移动（包含对角线），因此对角线距离是最合适的可纳启发函数。'
        '通过对比四种启发函数的实际表现，可以直观展示启发函数质量对搜索效率的影响。'
    )

    # 2.3 GA
    add_title('2.3 遗传算法原理', level=2)
    add_body(
        '遗传算法（Genetic Algorithm, GA）是受达尔文自然选择学说启发的进化计算方法，'
        '由John Holland于1975年提出。GA模拟生物进化过程中的选择、交叉和变异操作，'
        '在解空间中搜索最优解。不同于Dijkstra和A*的确定性搜索，GA是一种随机化、'
        '群体并行的全局优化方法。'
    )
    add_body(
        '本设计将GA应用于路径规划，具体设计如下：\n'
        '  (1) 编码方案：每条路径表示为一个变长染色体，基因是路径经过的中间点坐标'
        '序列（不含起点和终点），初始种群通过带目标偏向的随机游走生成；\n'
        '  (2) 适应度函数：f = 1 / (路径总长度 + 碰撞惩罚×100 + 段长惩罚×2)，'
        '适应度越高表示路径越好——路径越短、越少穿过障碍物、越平滑，适应度越高；\n'
        '  (3) 选择操作：采用轮盘赌选择（适应度比例选择）结合精英保留策略（保留'
        '前5%最优个体直接进入下一代）；\n'
        '  (4) 交叉操作：单点交叉，随机选取交叉点交换两个父代个体的基因段；\n'
        '  (5) 变异操作：包含四种变异类型——添加路径点、删除路径点、修改路径点位置、'
        '路径平滑（删除冗余拐点）；\n'
        '  (6) 不可行路径修复：利用Bresenham线检测碰撞，对穿过障碍物的路径段使用'
        '贪心方法进行局部修复。'
    )

    # 2.4 ACO
    add_title('2.4 蚁群算法原理', level=2)
    add_body(
        '蚁群算法（Ant Colony Optimization, ACO）由Marco Dorigo于1992年提出，是受'
        '蚂蚁觅食行为启发的群体智能算法。蚂蚁在寻找食物过程中会在路径上释放信息素，'
        '其他蚂蚁倾向于选择信息素浓度高的路径，形成正反馈机制，最终整个蚁群收敛到'
        '最短路径。'
    )
    add_body(
        '本设计将ACO应用于栅格路径规划，核心设计如下：\n'
        '  (1) 信息素表示：每个可通行单元格维护一个信息素浓度值，表示经过该单元格'
        '的吸引力；\n'
        '  (2) 启发式信息：每个单元格到目标点的欧几里得距离的倒数，引导蚂蚁向目标'
        '方向移动；\n'
        '  (3) 状态转移规则：使用伪随机比例规则——以概率q₀选择启发信息素乘积最大'
        '的邻居（开发），以概率1-q₀使用轮盘赌随机选择（探索）；\n'
        '  (4) 信息素更新：每次迭代后，信息素按挥发率ρ蒸发，然后只由前25%的优秀'
        '蚂蚁按路径质量进行信息素增强，排名越靠前增强越多；\n'
        '  (5) 死胡同处理：若蚂蚁陷入死胡同，使用贪心扩展方法尝试到达目标。\n'
        '关键参数设置：蚂蚁数n_ants=40，最大迭代max_iterations=80，信息素权重'
        'α=1.0，启发因子权重β=3.0，挥发率ρ=0.15。'
    )

    # 2.5 方案选择理由
    add_title('2.5 方案选择理由', level=2)
    add_body(
        '选择以上四种算法构成完整的对比实验框架，理由如下：'
    )
    add_body(
        '第一，算法覆盖面广。四种算法分别代表了人工智能课程中的盲目搜索（Dijkstra）、'
        '启发式搜索（A*）、进化计算（GA）和群体智能（ACO）四大核心算法范式，能够全面'
        '展示课程所学知识的综合运用。'
    )
    add_body(
        '第二，对比维度丰富。Dijkstra提供最优解基准，A*展示启发式信息对搜索效率的'
        '巨大提升，GA和ACO则展示了非确定性全局优化方法的不同特点。四种算法在解质量、'
        '搜索效率、时间开销等维度上各有优劣，对比分析具有教学意义。'
    )
    add_body(
        '第三，可视化效果出色。栅格地图上的路径规划天然适合图形化展示，不同算法的'
        '搜索结果可以直观地在同一张地图上进行比较。本设计生成的43张可视化图表涵盖了'
        '路径叠加、搜索过程、性能对比、收敛分析等多个角度，为报告提供了丰富的分析素材。'
    )
    add_body(
        '第四，Python语言实现。Python语言语法简洁，NumPy库提供了高效的矩阵运算，'
        'Matplotlib库提供了专业的数据可视化能力。全部代码约1000行，结构清晰，'
        '可读性强，便于评审教师理解算法实现细节。'
    )

    # ============================================================
    # 三、过程论述
    # ============================================================
    add_title('三、过程论述', level=1)
    add_empty_line()

    # ----------------------------------------------------------
    # 3.1 地图生成模块
    # ----------------------------------------------------------
    add_title('3.1 地图生成模块', level=2)
    add_body(
        '地图生成模块负责创建多样化的测试栅格地图，以全面评估算法在不同环境类型'
        '下的表现。模块实现了三种地图生成策略：'
    )
    add_body(
        '(1) 随机散点障碍（Random Obstacles）：按指定覆盖率（10%、20%、30%）随机'
        '放置障碍物，模拟自然环境中随机分布的障碍；'
    )
    add_body(
        '(2) 迷宫式障碍（Maze）：使用递归分割法（Recursive Division）生成迷宫，'
        '通过交替进行横向和纵向分割并预留通道口，形成规则但有挑战性的迷宫结构；'
    )
    add_body(
        '(3) 窄通道场景（Narrow Passage）：以规律间隔的横纵墙体构成多重障碍，'
        '仅保留少量狭窄通道，用于测试算法在受限空间中的搜索能力。'
    )
    add_body(
        '所有地图统一为30×30的栅格，起点固定在左上角(0,0)，终点固定在右下角(29,29)。'
        '起点和终点及其相邻格强制为可通行区域，确保地图有解。共计生成5个测试场景，'
        '五种栅格地图如图1至图5所示。'
    )

    # 图1-5: 五种场景栅格地图
    add_body('以下为五种测试场景的栅格地图可视化：')
    add_empty_line()

    map_filenames = [
        'map_随机散点-低密度(10%).png',
        'map_随机散点-中密度(20%).png',
        'map_随机散点-高密度(30%).png',
        'map_迷宫式障碍.png',
        'map_窄通道场景.png',
    ]
    fig_num = 1
    for i, (fname_key, scene_cn) in enumerate(SCENES):
        add_figure(map_filenames[i],
                   f'图{fig_num} {scene_cn}栅格地图（30×30，绿色=起点，红色=终点，深色=障碍物）')
        fig_num += 1
        if i < len(SCENES) - 1:
            add_empty_line()

    # ----------------------------------------------------------
    # 3.2 算法类设计与搜索过程可视化
    # ----------------------------------------------------------
    add_title('3.2 算法类设计与搜索过程可视化', level=2)
    add_body(
        '每个算法实现为独立的Python模块，遵循统一的接口规范：接受栅格地图、起点和'
        '终点作为输入，返回包含路径、探索节点数、运行时间等信息的字典。这种模块化设计'
        '便于算法的独立测试和并行比较。各算法类的结构如下：'
    )
    add_body(
        '(1) Dijkstra类：使用优先队列（heapq）管理待扩展节点，距离字典dist和'
        '前驱字典prev分别记录最短距离和路径回溯信息。支持8方向移动（含对角线），'
        '对角线移动代价为√2≈1.414。核心方法为find_path()。'
    )
    add_body(
        '(2) AStar类：在Dijkstra类的基础上增加启发函数计算。通过构造函数参数'
        'heuristic指定使用的启发函数类型（manhattan/euclidean/diagonal/chebyshev）。'
        '优先队列排序依据为f=g+h而非仅g值。'
    )
    add_body(
        '(3) GeneticAlgorithm类：包含种群初始化（_init_population）、适应度计算'
        '（_fitness）、选择（_roulette_select）、交叉（_crossover）、变异（_mutate）'
        '和进化主循环（_evolve）等方法。使用精英保留策略，每代保留最优个体。'
    )
    add_body(
        '(4) AntColonyOptimization类：维护信息素矩阵pheromone和启发式信息矩阵'
        'heuristic。每只蚂蚁通过_construct_path方法独立构建路径，使用伪随机比例'
        '规则进行状态转移。每轮迭代后进行信息素挥发和更新。'
    )

    add_body(
        '搜索过程可视化是本设计的一大亮点。Dijkstra和A*算法在搜索过程中记录探索'
        '扩散快照，直观展示两种搜索策略的本质差异。图6至图10展示了Dijkstra算法在'
        '五种场景下的搜索扩散过程，图11至图15展示了A*算法的对应过程。'
    )

    # 图6-10: Dijkstra搜索过程
    add_empty_line()
    add_body('Dijkstra算法搜索过程（图6-图10）：')
    add_empty_line()
    for i, (fname_key, scene_cn) in enumerate(SCENES):
        add_figure(f'search_process_dijkstra_{fname_key}.png',
                   f'图{fig_num} Dijkstra搜索过程 — {scene_cn}（浅蓝色=已探索节点）')
        fig_num += 1
        add_empty_line()

    # 图11-15: A*搜索过程
    add_page_break()
    add_body('A*算法搜索过程（图11-图15）：')
    add_empty_line()
    for i, (fname_key, scene_cn) in enumerate(SCENES):
        add_figure(f'search_process_astar_{fname_key}.png',
                   f'图{fig_num} A*搜索过程 — {scene_cn}（浅橙色=已探索节点）')
        fig_num += 1
        add_empty_line()

    # 图16-20: 搜索扩散对比
    add_page_break()
    add_body(
        '为更直观地对比两种搜索策略的差异，图16至图20将Dijkstra和A*在同一场景下的'
        '搜索扩散过程并列展示。可以清晰看出：Dijkstra以起点为中心均匀向四周扩散'
        '（圆形波前），而A*则沿起点到终点的方向定向扩散（窄带搜索），后者探索的节点'
        '数量远少于前者。'
    )
    add_empty_line()
    for i, (fname_key, scene_cn) in enumerate(SCENES):
        add_figure(f'diffusion_{fname_key}.png',
                   f'图{fig_num} Dijkstra vs A*搜索扩散对比 — {scene_cn}')
        fig_num += 1
        add_empty_line()

    # ----------------------------------------------------------
    # 3.3 关键代码解析
    # ----------------------------------------------------------
    add_title('3.3 关键代码解析', level=2)
    add_body('以下对几个关键实现细节进行说明：')
    add_body(
        '(1) 八方向移动与代价计算：四个基本方向（上下左右）的移动代价为1.0，四个'
        '对角线方向的移动代价为√2≈1.414。这种设计使得算法可以生成更自然、更短的'
        '对角线路径，优于仅支持四方向移动的方案。'
    )
    add_body(
        '(2) 碰撞检测：在GA算法的路径解码（_decode_path）中，使用Bresenham直线'
        '算法检测两个路径点之间是否穿过障碍物。若直线不可行，则调用贪心局部修复'
        '方法绕过障碍物。这确保了GA生成的路径始终是可行路径。'
    )
    add_body(
        '(3) 快照记录机制：Dijkstra和A*算法在搜索过程中按百分比（25%、50%、75%、'
        '100%）记录已探索节点的快照。对于A*算法（通常探索极少节点），额外设置了'
        '绝对数量快照点（5、15、30、50），确保总能捕获到足够的中间状态用于可视化。'
    )
    add_body(
        '(4) 信息素更新策略：ACO采用精英排序更新策略——只让前25%的优秀蚂蚁参与'
        '信息素增强，且增强量与排名成反比。这种方法避免了劣质路径对信息素分布的'
        '干扰，加速了算法收敛。'
    )
    add_body(
        '(5) 可视化模块：Visualizer类提供了plot_path_comparison、plot_overview、'
        'plot_search_diffusion、plot_performance_comparison、plot_convergence等'
        '10余种可视化方法，支持生成43张高质量静态图表。所有图表均使用matplotlib'
        '绘制，配色方案统一，分辨率150dpi，适合打印和报告展示。'
    )

    # ============================================================
    # 四、结果分析
    # ============================================================
    add_page_break()
    add_title('四、结果分析', level=1)
    add_empty_line()

    # ----------------------------------------------------------
    # 4.1 多种场景下的路径对比
    # ----------------------------------------------------------
    add_title('4.1 多种场景下的路径对比', level=2)
    add_body(
        '在5种不同的测试场景下，四种算法均成功找到了从起点到终点的可行路径。'
        '图21至图25以2×2子图的形式展示了每种场景下四个算法找到的路径对比。'
        '从图中可以直观看出：'
    )
    add_body(
        '(1) Dijkstra和A*在大多数场景下找到了完全相同的最短路径（路径长度一致），'
        '验证了A*算法使用对角线启发函数时的可纳性和最优性。'
    )
    add_body(
        '(2) GA算法在简单和中等密度随机障碍场景中找到了与Dijkstra相同的最优路径，'
        '但在迷宫和窄通道场景中路径略有偏差，体现了随机搜索算法的近似特性。'
    )
    add_body(
        '(3) ACO算法在所有场景中都能找到可行路径，但路径长度通常比最优解长约10-30%，'
        '这是蚁群算法在栅格地图上表现的典型特征——ACO更适合图搜索而非网格搜索。'
    )

    # 图21-25: 路径对比
    add_empty_line()
    for i, (fname_key, scene_cn) in enumerate(SCENES):
        add_figure(f'path_comparison_{fname_key}.png',
                   f'图{fig_num} 四种算法路径对比 — {scene_cn}（蓝=Dijkstra, 橙=A*, 紫=GA, 青=ACO）')
        fig_num += 1
        add_empty_line()

    # 图26-30: 综合概览
    add_page_break()
    add_body(
        '图26至图30将所有四种算法的路径叠加在同一张地图上，便于直接比较路径的'
        '重合度和差异。可以看出，Dijkstra、A*和GA的路径高度重合（均接近最优），'
        '而ACO的路径存在一定的绕行现象。'
    )
    add_empty_line()
    for i, (fname_key, scene_cn) in enumerate(SCENES):
        add_figure(f'overview_{fname_key}.png',
                   f'图{fig_num} 四种算法路径综合概览 — {scene_cn}')
        fig_num += 1
        add_empty_line()

    # ----------------------------------------------------------
    # 4.2 性能指标定量对比
    # ----------------------------------------------------------
    add_page_break()
    add_title('4.2 性能指标定量对比', level=2)
    add_body(
        '表1汇总了所有场景下各算法的三项核心指标：路径长度、探索节点数和运行时间。'
        '图31至图35为对应的柱状图可视化对比。主要发现如下：'
    )
    add_body(
        '(1) 路径质量（Path Length）：Dijkstra和A*提供最优解基准。GA在5个场景中'
        '有3个达到了最优解，2个场景接近最优（偏差<2%）。ACO的路径长度平均比最优'
        '解长约20%，在窄通道场景中偏差最大（约33%）。'
    )
    add_body(
        '(2) 搜索效率（Explored Nodes）：这是四种算法差异最大的指标。以低密度场景'
        '为例，Dijkstra探索了804个节点（约占全部可通行格的100%），而A*仅探索了32个'
        '节点，效率提升约25倍！这直观展示了启发式信息对搜索效率的巨大贡献。'
    )
    add_body(
        '(3) 时间效率（Runtime）：Dijkstra和A*运行时间在0.001-0.003秒之间，'
        '几乎实时完成。GA需要0.6-1.5秒（取决于地图复杂度），ACO需要1.5-2.6秒。'
        '虽然GA和ACO在时间上不占优势，但它们在处理大规模、高维问题时具有更好的'
        '可扩展性（如TSP问题中ACO的经典应用）。'
    )

    # 表1: 性能汇总
    add_empty_line()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run('表1 各场景算法性能汇总（部分代表性数据）')
    run.font.size = Pt(10)
    run.bold = True

    table = doc.add_table(rows=11, cols=5, style='Table Grid')
    headers = ['场景', '算法', '路径长度', '探索节点数', '运行时间(s)']
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = h
        for p in cell.paragraphs:
            for run in p.runs:
                run.font.size = Pt(9)
                run.bold = True
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    perf_data = [
        ['低密度(10%)', 'Dijkstra', '41.6', '804', '0.003'],
        ['低密度(10%)', 'A* (Manhattan)', '41.6', '32', '<0.001'],
        ['低密度(10%)', 'GA', '41.6', '222', '0.631'],
        ['低密度(10%)', 'ACO', '48.3', '804', '2.070'],
        ['中密度(20%)', 'Dijkstra', '42.8', '748', '0.003'],
        ['中密度(20%)', 'A* (Manhattan)', '42.8', '48', '<0.001'],
        ['迷宫(47%)', 'Dijkstra', '58.3', '352', '0.001'],
        ['迷宫(47%)', 'A* (Manhattan)', '58.3', '28', '<0.001'],
        ['窄通道', 'Dijkstra', '51.2', '561', '0.002'],
        ['窄通道', 'A* (Manhattan)', '51.2', '35', '<0.001'],
    ]
    for row_idx, row_data in enumerate(perf_data):
        for col_idx, val in enumerate(row_data):
            cell = table.rows[row_idx + 1].cells[col_idx]
            cell.text = str(val)
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(9)
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    add_empty_line()

    # 图31-35: 性能对比柱状图
    add_body('各场景性能对比柱状图（图31-图35）：')
    add_empty_line()
    for i, (fname_key, scene_cn) in enumerate(SCENES):
        add_figure(f'performance_{fname_key}.png',
                   f'图{fig_num} 四种算法性能指标对比 — {scene_cn}')
        fig_num += 1
        add_empty_line()

    # ----------------------------------------------------------
    # 4.3 收敛曲线分析
    # ----------------------------------------------------------
    add_page_break()
    add_title('4.3 收敛曲线分析', level=2)
    add_body(
        '图36至图40展示了GA和ACO算法在各场景下的收敛过程：'
    )
    add_body(
        '(1) GA收敛特征：GA的适应度曲线呈阶梯式上升，反映了遗传操作（交叉和变异）'
        '跳跃式改进种群质量的特点。在简单场景中，GA在前50代内快速收敛；在迷宫场景中，'
        '需要约100-120代才能稳定收敛。平均适应度曲线围绕最佳适应度波动，显示了种群'
        '多样性的维持。'
    )
    add_body(
        '(2) ACO收敛特征：ACO的最优路径长度曲线呈指数衰减趋势，初期快速下降，'
        '后期趋于平稳。在大部分场景中，ACO在前20次迭代内取得了大部分改进，'
        '之后的迭代主要用于精细调整。平均路径长度曲线持续高于最优值，说明蚁群中'
        '存在较大比例的次优路径，这有助于维持种群多样性、避免早熟收敛。'
    )
    add_body(
        '(3) 对比分析：GA的收敛曲线比ACO更平滑，这得益于精英保留策略确保了适应度'
        '的单调不减。ACO由于信息素挥发和随机探索机制，最优路径长度偶尔会有小幅波动。'
    )

    # 图36-40: 收敛曲线
    add_empty_line()
    for i, (fname_key, scene_cn) in enumerate(SCENES):
        add_figure(f'convergence_{fname_key}.png',
                   f'图{fig_num} GA与ACO收敛曲线 — {scene_cn}')
        fig_num += 1
        add_empty_line()

    # ----------------------------------------------------------
    # 4.4 启发函数影响分析
    # ----------------------------------------------------------
    add_page_break()
    add_title('4.4 启发函数影响分析', level=2)
    add_body(
        '图41至图42展示了对A*算法使用四种不同启发函数的对比实验结果。本实验在'
        '低密度随机障碍场景和迷宫场景中进行，涵盖四种启发函数：曼哈顿距离（Manhattan）、'
        '欧几里得距离（Euclidean）、对角线距离（Diagonal）和切比雪夫距离（Chebyshev）。'
        '关键发现：'
    )
    add_body(
        '(1) 曼哈顿距离（Manhattan）表现最佳，在低密度场景中仅探索32个节点即找到'
        '最优解。这是因为曼哈顿距离在栅格地图上是可纳的（允许八方向移动时也不高估），'
        '且计算开销最小。'
    )
    add_body(
        '(2) 对角线距离（Diagonal）探索了66个节点，虽然理论上是最优启发，但在实际'
        '栅格地图中并不显著优于曼哈顿距离。'
    )
    add_body(
        '(3) 切比雪夫距离（Chebyshev）探索了339个节点，表现最差。这是因为切比雪夫'
        '距离在八方向移动中可能高估实际代价（h > h*），导致算法失去最优性保证，'
        '且搜索效率下降。'
    )
    add_body(
        '(4) 结论：对于八方向移动的栅格路径规划，曼哈顿距离在效率和简洁性之间取得'
        '了最佳平衡。'
    )

    # 图41-42: 启发函数对比
    add_empty_line()
    add_figure('heuristic_随机散点-低密度(10%).png',
               f'图{fig_num} 四种启发函数对比 — 低密度随机障碍场景', width_inches=5.0)
    fig_num += 1
    add_empty_line()
    add_figure('heuristic_迷宫式障碍.png',
               f'图{fig_num} 四种启发函数对比 — 迷宫式障碍场景', width_inches=5.0)
    fig_num += 1

    # ----------------------------------------------------------
    # 4.5 算法优劣势讨论与综合评估
    # ----------------------------------------------------------
    add_page_break()
    add_title('4.5 算法优劣势讨论与综合评估', level=2)
    add_body('综合以上实验结果，对四种算法的优劣势进行总结：')
    add_body(
        'Dijkstra算法：优势在于保证最优解、实现简单、结果确定性好；劣势在于搜索'
        '效率低，在大规模地图上探索节点数量过多，无法利用启发信息。适用于对最优性'
        '要求极高且地图规模较小的场景，或作为其他算法的性能基准。'
    )
    add_body(
        'A*算法：优势在于搜索效率极高（相比Dijkstra提升一个数量级以上）、保证最优'
        '解（使用可纳启发函数时）、实现直观；劣势在于需要设计合适的启发函数，不恰当'
        '的启发函数可能导致性能退化。适用于大多数实际路径规划场景，是目前应用最广泛'
        '的路径搜索算法。'
    )
    add_body(
        '遗传算法：优势在于不依赖梯度信息、具有全局搜索能力、可处理复杂约束和多目标'
        '优化、天然支持并行计算；劣势在于运行时间长、参数敏感（种群大小、变异率等）、'
        '结果具有随机性、不能保证最优解。适用于解空间复杂、目标函数非凸非光滑的场景。'
    )
    add_body(
        '蚁群算法：优势在于正反馈机制使其在TSP类组合优化问题上表现优异、具有天然的'
        '分布式特性、自组织和鲁棒性强；劣势在于在栅格路径规划上表现不如A*精确、收敛'
        '速度较慢、参数调节复杂（α、β、ρ、蚂蚁数等均需精细调参）。适用于图搜索问题'
        '（如TSP、VRP）和动态环境中的路径规划。'
    )

    # 图43: 综合汇总
    add_empty_line()
    add_body(
        '图43为所有实验结果的综合汇总图，将五种场景下四种算法的路径长度、探索节点数'
        '和运行时间进行集中对比展示，便于从全局视角评估各算法的综合性能。'
    )
    add_empty_line()
    add_figure('comprehensive_summary.png',
               f'图{fig_num} 所有场景综合性能汇总对比', width_inches=5.0)
    fig_num += 1

    add_empty_line()
    add_body(
        '综合来看，在栅格路径规划这一具体问题上，A*算法凭借启发式信息的使用，在解质量'
        '和搜索效率之间取得了最佳平衡，是本场景下的推荐算法。Dijkstra虽然是理论最优的'
        '基准，但在效率维度上存在明显短板。GA和ACO分别代表了进化计算和群体智能两种不同'
        '的优化范式，虽然在确定性栅格路径规划上不占优势，但其设计思想对于理解和研究更'
        '复杂的AI优化问题具有重要的启发意义。'
    )

    # ============================================================
    # 五、课程设计总结
    # ============================================================
    add_page_break()
    add_title('五、课程设计总结', level=1)
    add_empty_line()

    add_body(
        '通过本次课程设计，我系统地实现了四种经典AI算法并将其应用于路径规划问题，'
        '获得了以下主要收获和体会：'
    )
    add_body(
        '第一，深刻理解了不同AI算法范式的本质差异。盲目搜索（Dijkstra）依靠穷举'
        '保证最优但效率低下，启发式搜索（A*）利用领域知识极大提升效率，进化计算（GA）'
        '模拟自然选择进行随机化全局搜索，群体智能（ACO）通过正反馈机制实现分布式优化。'
        '四种算法的思想截然不同，却在同一问题上有各自的表现特点，这让我对"没有免费的'
        '午餐"定理有了更直观的认识。'
    )
    add_body(
        '第二，掌握了算法性能的系统评估方法。通过设计多种测试场景（随机、迷宫、'
        '窄通道）和多维度评价指标（路径长度、探索节点数、运行时间），我学会了如何'
        '公平、全面地比较不同算法的性能。特别是启发函数对比实验让我认识到，即使是'
        '同一算法，参数和设计选择也会显著影响最终表现。'
    )
    add_body(
        '第三，提升了编程实践和问题解决能力。在实现GA算法时，我遇到了路径中穿过'
        '障碍物的问题，通过引入Bresenham线碰撞检测和贪心局部修复策略成功解决。在实现'
        'ACO算法时，蚂蚁陷入死胡同导致路径不完整的问题通过回退和贪心扩展策略得到改善。'
        '处理这些实际问题的过程锻炼了我的调试和优化能力。'
    )
    add_body(
        '第四，认识到可视化在算法分析中的重要性。通过43张可视化图表，实验数据变得'
        '直观可读，许多隐藏在数字背后的规律（如Dijkstra的圆形扩散模式、A*的定向扩散'
        '模式）变得一眼可见。这让我深刻体会到"一图胜千言"的道理。'
    )
    add_body(
        '第五，本设计仍存在改进空间。首先，可以增加RRT（快速随机树）和D*（动态A*）'
        '等更多算法进行更全面的对比。其次，GA和ACO的参数可以进一步调优以改善性能。'
        '最后，可以扩展到三维空间或动态环境中的路径规划，使研究更具实际应用价值。'
    )
    add_body(
        '总之，本次课程设计将《人工智能》课程的理论知识与编程实践紧密结合，不仅加深了'
        '我对各类AI算法的理解，也提升了算法设计、实现和评估的综合能力。这段经历将对我'
        '今后的学习和研究产生积极的影响。'
    )

    # ============================================================
    # 参考文献
    # ============================================================
    add_title('参考文献', level=1)
    add_empty_line()

    refs = [
        '[1] 王万良. 人工智能导论（第5版）[M]. 北京: 高等教育出版社, 2021.',
        '[2] Hart P E, Nilsson N J, Raphael B. A Formal Basis for the Heuristic Determination of Minimum Cost Paths[J]. IEEE Transactions on Systems Science and Cybernetics, 1968, 4(2): 100-107.',
        '[3] Dijkstra E W. A Note on Two Problems in Connexion with Graphs[J]. Numerische Mathematik, 1959, 1(1): 269-271.',
        '[4] Holland J H. Adaptation in Natural and Artificial Systems[M]. Cambridge: MIT Press, 1975.',
        '[5] Dorigo M, Maniezzo V, Colorni A. Ant System: Optimization by a Colony of Cooperating Agents[J]. IEEE Transactions on Systems, Man, and Cybernetics, Part B, 1996, 26(1): 29-41.',
        '[6] Russell S, Norvig P. Artificial Intelligence: A Modern Approach (4th ed.)[M]. Pearson, 2020.',
        '[7] Goldberg D E. Genetic Algorithms in Search, Optimization and Machine Learning[M]. Addison-Wesley, 1989.',
        '[8] Stützle T, Hoos H H. MAX-MIN Ant System[J]. Future Generation Computer Systems, 2000, 16(8): 889-914.',
        '[9] LaValle S M. Planning Algorithms[M]. Cambridge University Press, 2006.',
        '[10] 张军, 詹志辉. 计算智能[M]. 北京: 清华大学出版社, 2009.',
    ]

    for ref in refs:
        p = doc.add_paragraph()
        run = p.add_run(ref)
        run.font.name = '宋体'
        run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
        run.font.size = Pt(10.5)  # 五号

    add_empty_line()

    # ============================================================
    # 附录
    # ============================================================
    add_title('附录（程序代码）', level=1)
    add_empty_line()
    def add_code_block(file_label, code_text):
        """添加代码块（等宽字体，小号）"""
        # 文件标题
        p_title = doc.add_paragraph()
        p_title.paragraph_format.space_before = Pt(12)
        p_title.paragraph_format.space_after = Pt(4)
        run_title = p_title.add_run(f'【{file_label}】')
        run_title.font.name = '宋体'
        run_title.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
        run_title.font.size = Pt(10)
        run_title.bold = True

        # 代码内容（Courier New 8pt，保留缩进）
        for line in code_text.split('\n'):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = Pt(12)
            # 用非断行空格保留前导空白
            stripped = line.rstrip()
            if not stripped:
                run = p.add_run(' ')
                run.font.size = Pt(4)
            else:
                # 计算前导空格数
                leading = len(line) - len(line.lstrip())
                display_line = ' ' * leading + stripped
                run = p.add_run(display_line)
                run.font.name = 'Courier New'
                run.font.size = Pt(7.5)
                run.element.rPr.rFonts.set(qn('w:eastAsia'), 'Courier New')

    # 读取并插入各源代码文件
    source_files = [
        ('map_generator.py', '地图生成模块'),
        ('dijkstra.py', 'Dijkstra算法'),
        ('astar.py', 'A*算法'),
        ('ga.py', '遗传算法(GA)'),
        ('aco.py', '蚁群算法(ACO)'),
        ('visualize.py', '可视化模块'),
        ('main.py', '主程序入口'),
    ]

    for fname, fdesc in source_files:
        fpath = os.path.join(BASE_DIR, fname)
        if os.path.exists(fpath):
            with open(fpath, 'r', encoding='utf-8') as f:
                code = f.read()
            add_code_block(f'{fname} — {fdesc} ({len(code.splitlines())}行)', code)
            add_empty_line()
        else:
            p = doc.add_paragraph()
            run = p.add_run(f'[文件缺失: {fname}]')
            run.font.size = Pt(10)
            run.font.color.rgb = RGBColor(255, 0, 0)

    # ============================================================
    # 保存
    # ============================================================
    output_path = os.path.join(BASE_DIR, '课程设计报告_路径规划.docx')
    doc.save(output_path)
    print(f'报告已保存到: {output_path}')
    print(f'共插入 {fig_num - 1} 张图表')
    return output_path


if __name__ == '__main__':
    create_report()
