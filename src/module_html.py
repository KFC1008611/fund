# -*- coding: UTF-8 -*-
import re


def enhance_fund_tab_content(content, shares_map=None):
    """
    Enhance the fund tab content with operations panel, file operations, and shares input.
    Args:
        content: HTML content to enhance
        shares_map: Dict mapping fund_code -> shares value (optional)
    """
    # 添加文件操作和持仓统计区域
    file_operations = """
        <div class="file-operations" style="margin-bottom: 15px; display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
            <button class="btn btn-secondary" onclick="downloadFundMap()" style="padding: 8px 16px;"><i class="ri-download-cloud-2-line"></i> 导出基金列表</button>
            <input type="file" id="uploadFile" accept=".json" style="display:none" onchange="uploadFundMap(this.files[0])">
            <button class="btn btn-secondary" onclick="document.getElementById('uploadFile').click()" style="padding: 8px 16px;"><i class="ri-upload-cloud-2-line"></i> 导入基金列表</button>
            <span style="color: #f59e0b; font-size: 13px; margin-left: 10px;">
                <span style="color: #f59e0b;">⚠️</span> 导入/导出为覆盖性操作，直接应用最新配置（非累加）
            </span>
        </div>
    """

    # 添加持仓统计区域（将通过JavaScript动态填充）
    position_summary = """
        <div id="positionSummary" class="position-summary" style="display: none; background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 20px;">
            <h3 style="margin: 0 0 15px 0; font-size: 18px; font-weight: 600; color: var(--text-main); display: flex; justify-content: space-between; align-items: center;">
                <span><i class="ri-money-cny-box-line"></i> 持仓统计</span>
                <div style="display: flex; gap: 10px; align-items: center;">
                    <button id="showoffBtn" onclick="openShowoffCard()"
                            style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                   border: none; border-radius: 20px; padding: 6px 16px;
                                   color: white; font-size: 14px; font-weight: 600;
                                   cursor: pointer; display: flex; align-items: center; gap: 6px;
                                   box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
                                   transition: all 0.3s ease; white-space: nowrap;">
                        <i class="ri-magic-line"></i> 一键炫耀
                    </button>
                    <span id="toggleSensitiveValues" style="cursor: pointer; font-size: 18px; user-select: none;" title="显示 / 隐藏 收益明细"><i class="ri-eye-line"></i></span>
                </div>
            </h3>
            <div class="stats-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                <div class="stat-item">
                    <div style="font-size: 12px; color: var(--text-dim); margin-bottom: 5px;">总持仓金额</div>
                    <div id="totalValue" class="sensitive-value" style="font-size: 24px; font-weight: bold; color: var(--text-main);">
                        <span class="real-value">¥0.00</span><span class="hidden-value">****</span>
                    </div>
                </div>
                <div class="stat-item">
                    <div style="font-size: 12px; color: var(--text-dim); margin-bottom: 5px;">今日预估涨跌</div>
                    <div id="estimatedGain" style="font-size: 24px; font-weight: bold; white-space: nowrap; color: var(--text-main);">
                        <span class="sensitive-value"><span class="real-value">¥0.00</span><span class="hidden-value">****</span></span><span id="estimatedGainPct"> (+0.00%)</span>
                    </div>
                </div>
                <div class="stat-item">
                    <div style="font-size: 12px; color: var(--text-dim); margin-bottom: 5px;">今日实际涨跌(已结算部分)</div>
                    <div id="actualGain" style="font-size: 24px; font-weight: bold; white-space: nowrap; color: var(--text-main);">
                        <span class="sensitive-value"><span class="real-value">¥0.00</span><span class="hidden-value">****</span></span><span id="actualGainPct"> (+0.00%)</span>
                    </div>
                </div>
            </div>
        </div>

        <div id="fundDetailsSummary" class="fund-details-summary" style="display: none; background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 20px;">
            <h3 style="margin: 0 0 15px 0; font-size: 16px; font-weight: 600; color: var(--text-main);"><i class="ri-file-list-3-line"></i> 分基金涨跌明细</h3>
            <div style="overflow-x: auto;">
                <table id="fundDetailsTable" style="width: 100%; border-collapse: collapse; font-size: 13px;">
                    <thead>
                        <tr style="background: rgba(59, 130, 246, 0.1);">
                            <th style="padding: 10px; text-align: center; vertical-align: middle; color: var(--text-dim); font-weight: 500;">基金代码</th>
                            <th style="padding: 10px; text-align: center; vertical-align: middle; color: var(--text-dim); font-weight: 500;">基金名称</th>
                            <th style="padding: 10px; text-align: center; vertical-align: middle; color: var(--text-dim); font-weight: 500;">持仓份额</th>
                            <th class="sortable" onclick="sortTable(this.closest('table'), 3)" style="padding: 10px; text-align: center; vertical-align: middle; color: var(--text-dim); font-weight: 500; cursor: pointer; user-select: none;">持仓市值</th>
                            <th class="sortable" onclick="sortTable(this.closest('table'), 4)" style="padding: 10px; text-align: center; vertical-align: middle; color: var(--text-dim); font-weight: 500; cursor: pointer; user-select: none;">预估收益</th>
                            <th class="sortable" onclick="sortTable(this.closest('table'), 5)" style="padding: 10px; text-align: center; vertical-align: middle; color: var(--text-dim); font-weight: 500; cursor: pointer; user-select: none;">预估涨跌</th>
                            <th class="sortable" onclick="sortTable(this.closest('table'), 6)" style="padding: 10px; text-align: center; vertical-align: middle; color: var(--text-dim); font-weight: 500; cursor: pointer; user-select: none;">实际收益</th>
                            <th class="sortable" onclick="sortTable(this.closest('table'), 7)" style="padding: 10px; text-align: center; vertical-align: middle; color: var(--text-dim); font-weight: 500; cursor: pointer; user-select: none;">实际涨跌</th>
                        </tr>
                    </thead>
                    <tbody id="fundDetailsTableBody">
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 炫耀卡片模态框 -->
        <div id="showoffModal" class="showoff-modal" onclick="closeShowoffCard(event)">
            <div class="showoff-card" onclick="event.stopPropagation()">
                <!-- 关闭按钮 -->
                <button class="showoff-close" onclick="closeShowoffCard()">✕</button>

                <!-- 左上角品牌标识 -->
                <div class="showoff-brand-corner">
                    <img src="/static/1.ico" alt="Lan Fund" class="brand-logo" onerror="this.style.display='none'">
                    <span class="brand-name">Lan Fund</span>
                </div>

                <!-- 卡片背景装饰 -->
                <div class="showoff-bg-decoration">
                    <div class="bg-circle circle-1"></div>
                    <div class="bg-circle circle-2"></div>
                    <div class="bg-circle circle-3"></div>
                    <div class="bg-stars"></div>
                </div>

                <!-- 卡片头部 -->
                <div class="showoff-header">
                    <div class="showoff-icon">💰</div>
                    <h2 class="showoff-title">今日收益</h2>
                    <p class="showoff-date" id="showoffDate">2026-02-03</p>
                </div>

                <!-- 持仓统计摘要 -->
                <div class="showoff-summary">
                    <div class="summary-row summary-row-total">
                        <div class="summary-item">
                            <div class="summary-label">总持仓</div>
                            <div class="summary-value" id="showoffTotalValue">¥0.00</div>
                        </div>
                    </div>
                    <div class="summary-row">
                        <div class="summary-item">
                            <div class="summary-label">今日预估</div>
                            <div class="summary-value" id="showoffEstimatedGain">+¥0.00</div>
                        </div>
                        <div class="summary-item">
                            <div class="summary-label">今日实际</div>
                            <div class="summary-value" id="showoffActualGain">+¥0.00</div>
                        </div>
                    </div>
                </div>

                <!-- Top3基金明细 -->
                <div class="showoff-funds">
                    <div class="funds-header">
                        <span class="funds-title">🏆 收益Top3</span>
                    </div>
                    <div class="funds-list" id="showoffFundsList">
                        <!-- 动态生成 -->
                    </div>
                </div>
            </div>
        </div>
    """

    # 添加操作按钮面板 - 已移至每个基金行上
    # operations_panel = """
    #     <div class="fund-operations">
    #         <div class="operation-group">
    #             <button class="btn btn-success" onclick="openFundSelectionModal('hold')"><i class="ri-star-line"></i> 标记持有</button>
    #             <button class="btn btn-secondary" onclick="openFundSelectionModal('unhold')"><i class="ri-star-off-line"></i> 取消持有</button>
    #             <button class="btn btn-info" onclick="openFundSelectionModal('sector')"><i class="ri-price-tag-3-line"></i> 标注板块</button>
    #             <button class="btn btn-warning" onclick="openFundSelectionModal('unsector')"><i class="ri-price-tag-2-line"></i> 删除板块</button>
    #             <button class="btn btn-danger" onclick="openFundSelectionModal('delete')"><i class="ri-delete-bin-line"></i> 删除基金</button>
    #         </div>
    #     </div>
    # """
    operations_panel = ""  # 操作按钮已移至每个基金行上

    # 简化的添加基金输入框
    add_fund_area = """
        <div class="add-fund-input">
            <input type="text" id="fundCodesInput" placeholder="输入基金代码（逗号分隔，如：016858,007872）">
            <button class="btn btn-primary" onclick="addFunds()">添加</button>
        </div>
    """

    # 在"近30天"列后添加"持仓份额"和"操作"列
    content = re.sub(
        r"(<th[^>]*>近30天</th>)",
        r"\1\n                    <th>持仓份额</th>\n                    <th style=\"text-align: center;\">操作</th>",
        content,
        count=1,
    )

    # 在每个数据行添加份额输入框
    # 先找到所有表格行，然后在包含基金代码的行末尾添加份额输入框
    def add_shares_to_row(match):
        row_content = match.group(0)
        # 从行内容中提取第一个6位数字（基金代码）- 假设第一列是基金代码
        code_match = re.search(r"<td[^>]*>(\d{6})</td>", row_content)
        if code_match:
            fund_code = code_match.group(1)

            # 根据份额数据确定按钮状态
            shares = 0
            if shares_map and fund_code in shares_map:
                try:
                    shares = float(shares_map[fund_code])
                except (ValueError, TypeError):
                    shares = 0

            # 根据份额值设置按钮文本和颜色
            if shares > 0:
                button_text = "修改"
                button_color = "#10b981"  # 绿色
            else:
                button_text = "设置"
                button_color = "#3b82f6"  # 蓝色

            operation_buttons = f"""
                <button onclick="event.stopPropagation(); window.selectedFundCode='{fund_code}'; openFundSelectionModal('hold');" 
                        title="标记持有" 
                        class="fund-row-ops-btn" style="background: #10b981;">
                    <i class="ri-star-line"></i>
                </button>
                <button onclick="event.stopPropagation(); window.selectedFundCode='{fund_code}'; openFundSelectionModal('unhold');" 
                        title="取消持有" 
                        class="fund-row-ops-btn" style="background: #6b7280;">
                    <i class="ri-star-off-line"></i>
                </button>
                <button onclick="event.stopPropagation(); window.selectedFundCode='{fund_code}'; openFundSelectionModal('sector');" 
                        title="标注板块" 
                        class="fund-row-ops-btn" style="background: #3b82f6;">
                    <i class="ri-price-tag-3-line"></i>
                </button>
                <button onclick="event.stopPropagation(); window.selectedFundCode='{fund_code}'; openFundSelectionModal('unsector');" 
                        title="删除板块" 
                        class="fund-row-ops-btn" style="background: #f59e0b;">
                    <i class="ri-price-tag-2-line"></i>
                </button>
                <button onclick="event.stopPropagation(); window.selectedFundCode='{fund_code}'; openFundSelectionModal('delete');" 
                        title="删除基金" 
                        class="fund-row-ops-btn" style="background: #ef4444;">
                    <i class="ri-delete-bin-line"></i>
                </button>
            """

            row_with_shares = (
                row_content[:-5]
                + f"""<td>
                <button class="shares-button" id="sharesBtn_{fund_code}"
                        onclick="openSharesModal('{fund_code}')"
                        style="padding: 6px 12px; background: {button_color}; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; transition: all 0.2s;">
                    {button_text}
                </button>
            </td>
            <td style="text-align: center; white-space: nowrap;">
                {operation_buttons}
            </td></tr>"""
            )
            return row_with_shares
        return row_content

    # 匹配完整的表格行（非贪婪匹配行内容）
    content = re.sub(r"<tr>.*?</tr>", add_shares_to_row, content, flags=re.DOTALL)

    return (
        file_operations + position_summary + operations_panel + add_fund_area + content
    )


def get_table_html(title, data, sortable_columns=None):
    """
    生成单个表格的HTML代码。
    :param title: list, 表头标题列表。
    :param data: list of lists, 表格数据。
    :param sortable_columns: list, 可排序的列的索引 (从0开始)。例如 [1, 2, 3]
    """
    if sortable_columns is None:
        sortable_columns = []

    ths = []
    for i, col_name in enumerate(title):
        if i in sortable_columns:
            ths.append(
                f'<th class="sortable" onclick="sortTable(this.closest(\'table\'), {i})">{col_name}</th>'
            )
        else:
            ths.append(f"<th>{col_name}</th>")

    thead_html = f"""
    <thead>
        <tr>
            {"".join(ths)}
        </tr>
    </thead>
    """

    tbody_rows = []
    for row_data in data:
        tds = [f"<td>{x}</td>" for x in row_data]
        tbody_rows.append(f"<tr>{''.join(tds)}</tr>")

    tbody_html = f"""
    <tbody>
        {"".join(tbody_rows)}
    </tbody>
    """

    return f"""
    <div class="table-container">
        <table class="style-table">
            {thead_html}
            {tbody_html}
        </table>
    </div>
    """


def generate_holdings_cards_html(fund_data_map):
    """
    Generate holdings cards HTML for funds marked as held.
    :param fund_data_map: dict, mapping of fund code to fund data
    :return: str, HTML for holdings cards section
    """
    # Filter held funds
    held_funds = []
    for code, data in fund_data_map.items():
        if data.get("is_hold", False):
            held_funds.append((code, data))

    if not held_funds:
        return ""

    cards_html = []
    for code, data in held_funds:
        fund_name = data.get("fund_name", "Unknown")
        sectors = data.get("sectors", [])

        # Generate sector tags with icon and gray text (like delete sector popup)
        sector_tags = (
            f'<span style="color: #8b949e; font-size: 12px;"> 🏷️ {", ".join(sectors)}</span>'
            if sectors
            else ""
        )

        # Card HTML
        card_html = f"""
        <div class="holding-card" data-code="{code}">
            <div class="holding-card-header">
                <div class="holding-card-title">
                    <div class="holding-card-code">{code}</div>
                    <div class="holding-card-name">{fund_name}</div>
                    {f'<div class="holding-card-sectors">{sector_tags}</div>' if sectors else ""}
                </div>
                <div class="holding-card-badge">⭐</div>
            </div>
            <div class="holding-card-metrics">
                <div class="holding-metric">
                    <div class="holding-metric-label">净值</div>
                    <div class="holding-metric-value" id="card-netvalue-{code}">--</div>
                </div>
                <div class="holding-metric">
                    <div class="holding-metric-label">估值增长</div>
                    <div class="holding-metric-value" id="card-estimated-{code}">--</div>
                </div>
                <div class="holding-metric">
                    <div class="holding-metric-label">日涨幅</div>
                    <div class="holding-metric-value" id="card-daygrowth-{code}">--</div>
                </div>
                <div class="holding-metric">
                    <div class="holding-metric-label">持仓市值</div>
                    <div class="holding-metric-value" id="card-position-{code}">¥0.00</div>
                </div>
            </div>
            <div class="holding-card-footer">
                <div class="holding-footer-item">
                    <div class="holding-footer-label">连涨/跌</div>
                    <div class="holding-footer-value" id="card-consecutive-{code}">--</div>
                </div>
                <div class="holding-footer-item">
                    <div class="holding-footer-label">近30天</div>
                    <div class="holding-footer-value" id="card-monthly-{code}">--</div>
                </div>
                <div class="holding-footer-item">
                    <div class="holding-footer-label">份额</div>
                    <div class="holding-footer-value">
                        <input type="number" step="0.01" min="0"
                               id="card-shares-{code}"
                               class="shares-input"
                               data-code="{code}"
                               placeholder="0"
                               value=""
                               style="width: 60px; padding: 2px 4px; border: 1px solid var(--border); border-radius: 4px; font-size: 11px; background: var(--card-bg); color: var(--text-main);"
                               onchange="updateShares('{code}', this.value)">
                    </div>
                </div>
            </div>
        </div>
        """
        cards_html.append(card_html)

    return f"""
    <div class="holdings-section">
        <div class="holdings-header">
            <div class="holdings-title">💎 Core Holdings</div>
            <div class="holdings-count">{len(held_funds)} Positions</div>
        </div>
        <div class="holdings-grid">
            {"".join(cards_html)}
        </div>
    </div>
    """


def generate_terminal_dashboard_html():
    """
    Generate the Terminal Dashboard HTML (will be populated by JavaScript).
    """
    return """
    <div class="terminal-dashboard" id="terminalDashboard" style="display: none;">
        <div class="stat-group">
            <label>今日预估收益 (EST. TODAY)</label>
            <div class="big-num" id="dashEstGain">¥0.00</div>
            <div class="stat-change" id="dashEstGainPct">0.00% ↑</div>
        </div>
        <div class="stat-group">
            <label>持仓市值 (MARKET VALUE)</label>
            <div class="big-num" id="dashTotalValue">¥0.00</div>
            <div class="stat-change" id="dashHoldingCount">0 只持有中</div>
        </div>
        <div class="stat-group">
            <label>昨日结算 (SETTLED)</label>
            <div class="big-num" id="dashActualGain">¥0.00</div>
            <div class="stat-change" id="dashActualGainPct">0.00% ↓</div>
        </div>
    </div>
    """


def get_full_page_html_sidebar(tabs_data, username=None):
    """Generate full page HTML with sidebar navigation"""
    js_script = get_javascript_code()
    css_style = get_css_style()

    # Get fund data for holdings/watchlist sections
    fund_map = {}
    for tab in tabs_data:
        if tab["id"] == "fund":
            # Extract fund_map from fund tab - will be passed from fund_server.py
            fund_map = tab.get("fund_map", {})
            break

    # Generate sections for other tabs (hidden by default)
    other_sections_html = ""
    for tab in tabs_data:
        if tab["id"] != "fund":
            tab_id = tab["id"]
            tab_title = tab["title"]
            other_sections_html += f'''
                <section class="content-section hidden" id="{tab_id}Section">
                    <div class="section-header">
                        <h2 class="section-heading">{tab_title}</h2>
                    </div>
                    <div class="section-content" id="{tab_id}Content"></div>
                </section>
            '''

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LanFund Terminal</title>
    {css_style}
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <!-- Navbar with logo and quote -->
    <nav class="navbar">
        <div class="navbar-brand">
            <img src="/static/1.ico" alt="Logo" class="navbar-logo">
        </div>
        <div class="navbar-quote">
            偶然与巧合, 舞动了蝶翼, 谁的心头风起 ————《如果我们不曾相遇》
        </div>
        <div class="navbar-menu">
            <span class="navbar-item">实时行情</span>
            {f'<span class="navbar-item" style="color: #3b82f6;">🍎 {username}</span>' if username else ""}
            {f'<a href="/logout" class="navbar-item" style="color: #f85149; text-decoration: none;">退出登录</a>' if username else ""}
        </div>
    </nav>

    <!-- App Container with Sidebar -->
    <div class="app-container-sidebar">
        {get_sidebar_navigation_html()}

        <main class="main-content-area">
            {get_header_bar_html()}
            {get_summary_bar_html()}

            <div class="content-body" id="contentBody">
                <!-- Holdings & Watchlist Sections -->
                {generate_holdings_section_html(fund_map)}
                {generate_watchlist_section_html(fund_map)}

                <!-- Other tab sections (hidden by default) -->
                {other_sections_html}
            </div>
        </main>
    </div>

    <!-- Modals (preserved) -->
    <!-- 板块选择对话框 -->
    <div class="sector-modal" id="sectorModal">
        <div class="sector-modal-content">
            <div class="sector-modal-header">选择板块</div>
            <input type="text" class="sector-modal-search" id="sectorSearch" placeholder="搜索板块名称...">
            <div id="sectorCategories">
                <!-- 板块分类将通过JS动态生成 -->
            </div>
            <div class="sector-modal-footer">
                <button class="btn btn-secondary" onclick="closeSectorModal()">取消</button>
                <button class="btn btn-primary" onclick="confirmSector()">确定</button>
            </div>
        </div>
    </div>

    <!-- 基金选择对话框 -->
    <div class="sector-modal" id="fundSelectionModal">
        <div class="sector-modal-content">
            <div class="sector-modal-header" id="fundSelectionTitle">选择基金</div>
            <input type="text" class="sector-modal-search" id="fundSelectionSearch" placeholder="搜索基金代码或名称...">
            <div id="fundSelectionList" style="max-height: 400px; overflow-y: auto;">
                <!-- 基金列表将通过JS动态生成 -->
            </div>
            <div class="sector-modal-footer">
                <button class="btn btn-secondary" onclick="closeFundSelectionModal()">取消</button>
                <button class="btn btn-primary" id="fundSelectionConfirmBtn" onclick="confirmFundSelection()">确定</button>
            </div>
        </div>
    </div>

    <!-- 确认对话框 -->
    <div class="confirm-dialog" id="confirmDialog">
        <div class="confirm-dialog-content">
            <h3 id="confirmTitle" class="confirm-title"></h3>
            <p id="confirmMessage" class="confirm-message"></p>
            <div class="confirm-actions">
                <button class="btn btn-secondary" onclick="closeConfirmDialog()">取消</button>
                <button class="btn btn-primary" id="confirmBtn">确定</button>
            </div>
        </div>
    </div>

    <!-- 份额设置弹窗 -->
    <div class="sector-modal" id="sharesModal">
        <div class="sector-modal-content" style="max-width: 400px;">
            <div class="sector-modal-header">设置持仓份额</div>
            <div style="padding: 20px;">
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 8px; color: var(--text-main); font-weight: 500;">基金代码</label>
                    <div id="sharesModalFundCode" style="padding: 10px; background: rgba(59, 130, 246, 0.1); border-radius: 6px; color: #3b82f6; font-weight: 600; font-family: monospace;"></div>
                </div>
                <div style="margin-bottom: 15px;">
                    <label for="sharesModalInput" style="display: block; margin-bottom: 8px; color: var(--text-main); font-weight: 500;">持仓份额</label>
                    <input type="number" id="sharesModalInput" step="0.01" min="0" placeholder="请输入份额"
                           style="width: 100%; padding: 10px 12px; border: 1px solid var(--border); border-radius: 6px; font-size: 14px; background: var(--card-bg); color: var(--text-main);">
                </div>
            </div>
            <div class="sector-modal-footer">
                <button class="btn btn-secondary" onclick="closeSharesModal()">取消</button>
                <button class="btn btn-primary" onclick="confirmShares()">确定</button>
            </div>
        </div>
    </div>

    {js_script}
    <script src="/static/js/main.js"></script>
    <script src="/static/js/sidebar-nav.js"></script>
</body>
</html>"""

    return html


def get_full_page_html(tabs_data, username=None, use_sidebar=False):
    # Use new sidebar layout if requested
    if use_sidebar:
        return get_full_page_html_sidebar(tabs_data, username)

    js_script = get_javascript_code()
    css_style = get_css_style()

    # Generate Tab Headers
    tab_headers = []
    tab_contents = []

    # Check if tabs_data is a list of dicts (new format) or list of strings (old format fallback)
    if (
        isinstance(tabs_data, list)
        and len(tabs_data) > 0
        and isinstance(tabs_data[0], str)
    ):
        # Fallback for old format
        return f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>LanFund Dashboard</title>
            {css_style}
        </head>
        <body>
            <div class="app-container">
                <div class="main-content">
                    <div class="dashboard-grid">
                        {"".join(tabs_data)}
                    </div>
                </div>
            </div>
            {js_script}
        </body>
        </html>
        """

    for index, tab in enumerate(tabs_data):
        is_active = "active" if index == 0 else ""
        tab_id = tab["id"]
        tab_title = tab["title"]
        content = tab["content"]

        tab_headers.append(f"""
            <button class="tab-button {is_active}" onclick="openTab(event, '{tab_id}')">
                {tab_title}
            </button>
        """)

        # 为"自选基金"标签页添加操作区域
        if tab_id == "fund":
            # 使用 enhance_fund_tab_content 函数来添加操作区域（避免重复代码）
            enhanced_content = enhance_fund_tab_content(content)
        else:
            enhanced_content = content

        tab_contents.append(f"""
            <div id="{tab_id}" class="tab-content {is_active}">
                {enhanced_content}
            </div>
        """)

    # Check if we have actual data or if this is initial SSE setup
    has_data = (
        tabs_data and len(tabs_data) > 0 and tabs_data[0].get("content", "").strip()
    )

    if not has_data:
        # Return SSE-enabled loading page
        return get_sse_loading_page(css_style, js_script)

    return f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
        <meta http-equiv="Pragma" content="no-cache">
        <meta http-equiv="Expires" content="0">
        <title>LanFund Dashboard</title>
        {css_style}
    </head>
    <body>
        <nav class="navbar">
            <div class="navbar-brand">BuBu Fund LanFund助手</div>
            <div class="navbar-menu">
                <span class="navbar-item">实时行情</span>
                {f'<span class="navbar-item" style="color: #3b82f6;">🍎 {username}</span>' if username else ""}
                {f'<a href="/logout" class="navbar-item" style="color: #f85149; text-decoration: none;">退出登录</a>' if username else ""}
            </div>
        </nav>
        
        <div class="app-container">
            <div class="main-content">
                <div class="tabs-header">
                    {"".join(tab_headers)}
                </div>
                <div class="dashboard-grid">
                    {"".join(tab_contents)}
                </div>
            </div>
        </div>

        <!-- 板块选择对话框 -->
        <div class="sector-modal" id="sectorModal">
            <div class="sector-modal-content">
                <div class="sector-modal-header">选择板块</div>
                <input type="text" class="sector-modal-search" id="sectorSearch" placeholder="搜索板块名称...">
                <div id="sectorCategories">
                    <!-- 板块分类将通过JS动态生成 -->
                </div>
                <div class="sector-modal-footer">
                    <button class="btn btn-secondary" onclick="closeSectorModal()">取消</button>
                    <button class="btn btn-primary" onclick="confirmSector()">确定</button>
                </div>
            </div>
        </div>

        <!-- 基金选择对话框 -->
        <div class="sector-modal" id="fundSelectionModal">
            <div class="sector-modal-content">
                <div class="sector-modal-header" id="fundSelectionTitle">选择基金</div>
                <input type="text" class="sector-modal-search" id="fundSelectionSearch" placeholder="搜索基金代码或名称...">
                <div id="fundSelectionList" style="max-height: 400px; overflow-y: auto;">
                    <!-- 基金列表将通过JS动态生成 -->
                </div>
                <div class="sector-modal-footer">
                    <button class="btn btn-secondary" onclick="closeFundSelectionModal()">取消</button>
                    <button class="btn btn-primary" id="fundSelectionConfirmBtn" onclick="confirmFundSelection()">确定</button>
                </div>
            </div>
        </div>

        <!-- 确认对话框 -->
        <div class="confirm-dialog" id="confirmDialog">
            <div class="confirm-dialog-content">
                <h3 id="confirmTitle" class="confirm-title"></h3>
                <p id="confirmMessage" class="confirm-message"></p>
                <div class="confirm-actions">
                    <button class="btn btn-secondary" onclick="closeConfirmDialog()">取消</button>
                    <button class="btn btn-primary" id="confirmBtn">确定</button>
                </div>
            </div>
        </div>

        {js_script}
    </body>
    </html>
    """


def get_sse_loading_page(css_style, js_script):
    """Return a loading page that will be updated via SSE"""
    return f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LanFund Dashboard - Loading</title>
        {css_style}
        <style>
            .loading-container {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100%;
                padding: 2rem;
            }}
            .navbar-brand {{
                display: flex;
                align-items: center;
            }}
            .navbar-logo {{
                width: 32px;
                height: 32px;
                margin-right: 12px;
            }}
            .loading-spinner {{
                border: 4px solid #f3f3f3;
                border-top: 4px solid var(--bloomberg-blue);
                border-radius: 50%;
                width: 50px;
                height: 50px;
                animation: spin 1s linear infinite;
            }}
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            .loading-status {{
                margin-top: 1rem;
                font-size: 0.9rem;
                color: #666;
            }}
            .task-list {{
                margin-top: 1rem;
                max-width: 400px;
            }}
            .task-item {{
                padding: 0.5rem;
                margin: 0.3rem 0;
                border-radius: 4px;
                background: #f5f5f5;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .task-item.completed {{
                background: #d4edda;
                color: #155724;
            }}
            .task-item.error {{
                background: #f8d7da;
                color: #721c24;
            }}
        </style>
    </head>
    <body>
        <nav class="navbar">
            <div class="navbar-brand">
                <img src="/static/1.ico" alt="Logo" class="navbar-logo">
                <span>BuBu Fund LanFund助手</span>
            </div>
            <div class="navbar-menu">
                <span class="navbar-item">加载中...</span>
            </div>
        </nav>
        
        <div class="app-container">
            <div class="main-content">
                <div class="loading-container">
                    <div class="loading-spinner"></div>
                    <div class="loading-status" id="status">正在连接数据源...</div>
                    <div class="task-list" id="task-list"></div>
                </div>
            </div>
        </div>

        <script>
        const eventSource = new EventSource('/fund' + window.location.search);
        const taskList = document.getElementById('task-list');
        const statusEl = document.getElementById('status');
        const taskElements = {{}};

        eventSource.addEventListener('message', function(e) {{
            try {{
                const data = JSON.parse(e.data);
                
                if (data.type === 'init') {{
                    statusEl.textContent = '正在加载数据模块...';
                    data.tasks.forEach(taskName => {{
                        const taskEl = document.createElement('div');
                        taskEl.className = 'task-item';
                        taskEl.innerHTML = `<span>${{getTaskTitle(taskName)}}</span><span>⏳</span>`;
                        taskList.appendChild(taskEl);
                        taskElements[taskName] = taskEl;
                    }});
                }}
                else if (data.type === 'task_complete') {{
                    if (taskElements[data.name]) {{
                        taskElements[data.name].className = 'task-item completed';
                        taskElements[data.name].querySelector('span:last-child').textContent = '✓';
                    }}
                }}
                else if (data.type === 'error') {{
                    if (taskElements[data.name]) {{
                        taskElements[data.name].className = 'task-item error';
                        taskElements[data.name].querySelector('span:last-child').textContent = '✗';
                    }}
                }}
                else if (data.type === 'complete') {{
                    statusEl.textContent = '加载完成！正在渲染页面...';
                    eventSource.close();
                    // Replace entire page with the complete HTML
                    document.open();
                    document.write(data.html);
                    document.close();
                }}
            }} catch (err) {{
                console.error('SSE parse error:', err);
            }}
        }});

        eventSource.addEventListener('error', function(e) {{
            statusEl.textContent = '连接错误，正在重试...';
            console.error('SSE error:', e);
        }});

        function getTaskTitle(taskName) {{
            const titles = {{
                'kx': '7*24快讯',
                'marker': '全球指数',
                'real_time_gold': '实时贵金属',
                'gold': '历史金价',
                'seven_A': '成交量趋势',
                'A': '上证分时',
                'fund': '自选基金',
                'bk': '行业板块'
            }};
            return titles[taskName] || taskName;
        }}
        </script>
    </body>
    </html>
    """


def get_sidebar_navigation_html():
    """Generate 70px sidebar with 9 section icons"""
    sections = [
        {"id": "news", "icon": "ri-newspaper-line", "label": "快讯", "tab_id": "kx"},
        {
            "id": "indices",
            "icon": "ri-bar-chart-2-line",
            "label": "指数",
            "tab_id": "marker",
        },
        {
            "id": "gold-realtime",
            "icon": "ri-vip-diamond-line",
            "label": "贵金属",
            "tab_id": "real_time_gold",
        },
        {
            "id": "gold-history",
            "icon": "ri-line-chart-line",
            "label": "金价",
            "tab_id": "gold",
        },
        {
            "id": "volume",
            "icon": "ri-bar-chart-grouped-line",
            "label": "成交量",
            "tab_id": "seven_A",
        },
        {"id": "timing", "icon": "ri-time-line", "label": "分时", "tab_id": "A"},
        {
            "id": "funds",
            "icon": "ri-briefcase-4-line",
            "label": "基金",
            "tab_id": "fund",
        },
        {
            "id": "sectors",
            "icon": "ri-building-4-line",
            "label": "板块",
            "tab_id": "bk",
        },
        {
            "id": "query",
            "icon": "ri-search-2-line",
            "label": "查询",
            "tab_id": "select_fund",
        },
    ]

    html = '<aside class="sidebar-nav" id="sidebarNav">\n'
    html += '  <div class="sidebar-icons">\n'

    for i, section in enumerate(sections):
        active = " active" if i == 6 else ""  # funds section active by default
        html += f'''    <button class="sidebar-icon{active}" data-section="{section["id"]}" data-tab-id="{section["tab_id"]}">
      <i class="{section["icon"]}" style="font-size: 20px;"></i>
      <span class="icon-label">{section["label"]}</span>
    </button>\n'''

    html += """    <button class="sidebar-toggle" id="sidebarToggle">
      <span><i class="ri-arrow-right-s-line"></i></span>
      <span class="toggle-text">展开</span>
    </button>
"""
    html += "  </div>\n"
    html += "</aside>\n"

    return html


def get_header_bar_html(section_title="自选基金"):
    """Generate header bar with section title and market status"""
    return f"""<header class="content-header">
  <div class="header-left">
    <h1 class="section-title" id="sectionTitle">{section_title}</h1>
    <span class="market-status">
      <span class="status-dot"></span>
      <span id="marketStatusText">市场开盘中</span>
    </span>
  </div>
  <div class="header-right">
    <span class="last-update" id="lastUpdate">更新于 --:--:--</span>
  </div>
</header>"""


def get_summary_bar_html():
    """Generate 4-column summary bar (populated by JavaScript)"""
    return """<section class="summary-bar" id="summaryBar">
  <div class="summary-card">
    <div class="summary-label">总持仓</div>
    <div class="summary-value" id="summaryTotalValue">¥0.00</div>
    <div class="summary-change neutral" id="summaryTotalChange">--</div>
  </div>
  <div class="summary-card">
    <div class="summary-label">今日预估</div>
    <div class="summary-value" id="summaryEstGain">¥0.00</div>
    <div class="summary-change neutral" id="summaryEstChange">+0.00%</div>
  </div>
  <div class="summary-card">
    <div class="summary-label">已结算</div>
    <div class="summary-value" id="summaryActualGain">¥0.00</div>
    <div class="summary-change neutral" id="summaryActualChange">+0.00%</div>
  </div>
  <div class="summary-card">
    <div class="summary-label">持仓数量</div>
    <div class="summary-value" id="summaryHoldCount">0 只</div>
    <div class="summary-change neutral">已标记</div>
  </div>
</section>"""


def generate_fund_row_html(fund_code, fund_data, is_held=True):
    """Generate a single fund row (replaces holdings cards)"""
    import html

    # Extract fund data
    name = fund_data.get("fund_name", "")
    sectors = fund_data.get("sectors", [])
    shares = fund_data.get("shares", 0)

    # Escape fund_code and name for safe HTML/JavaScript usage
    safe_code = html.escape(str(fund_code))
    safe_name = html.escape(str(name))

    # Build sector tags
    sector_tags = ""
    if is_held:
        sector_tags += (
            '<span class="tag tag-hold"><i class="ri-star-fill"></i> 持有</span>'
        )
    if sectors:
        # Display sectors with icon and gray text (like delete sector popup style)
        safe_sectors = html.escape(", ".join(str(s) for s in sectors))
        sector_tags += f'<span style="color: #8b949e; font-size: 12px;"> <i class="ri-price-tag-3-line"></i> {safe_sectors}</span>'

    # Shares input (only for held funds)
    shares_html = ""
    if is_held:
        shares_html = (
            f'<div class="metric metric-shares">'
            f'<span class="metric-label">持仓份额</span>'
            f'<input type="number" class="shares-input" id="shares_{safe_code}" '
            f'value="{shares}" step="0.01" min="0" '
            f"onchange=\"updateShares('{safe_code}', this.value)\">"
            f"</div>"
        )

    return (
        f'<div class="fund-row" data-code="{safe_code}">'
        f'<div class="fund-row-main">'
        f'<div class="fund-info">'
        f'<div class="fund-code-name">'
        f'<span class="fund-code">{safe_code}</span>'
        f'<span class="fund-name">{safe_name}</span>'
        f"</div>"
        f'<div class="fund-tags">{sector_tags}</div>'
        f"</div>"
        f'<div class="fund-metrics" id="metrics_{safe_code}">'
        f"<!-- Metrics populated by JavaScript -->"
        f'<div class="metric"><span class="metric-label">净值</span><span class="metric-value">--</span></div>'
        f'<div class="metric"><span class="metric-label">估值增长</span><span class="metric-value">--</span></div>'
        f'<div class="metric"><span class="metric-label">日涨幅</span><span class="metric-value">--</span></div>'
        f'<div class="metric"><span class="metric-label">连涨/跌</span><span class="metric-value">--</span></div>'
        f'<div class="metric"><span class="metric-label">近30天</span><span class="metric-value">--</span></div>'
        f"{shares_html}"
        f"</div>"
        f"</div>"
        f'<div class="fund-row-actions">'
        f'<button class="btn-icon" onclick="toggleFundExpand(\'{safe_code}\')" title="展开/收起">'
        f'<span><i class="ri-arrow-down-s-line"></i></span>'
        f"</button>"
        f"</div>"
        f"</div>"
    )


def generate_holdings_section_html(fund_map):
    """Generate Core Holdings section with held funds"""
    held_funds = {
        code: data for code, data in fund_map.items() if data.get("is_hold", False)
    }

    html = (
        """<section class="content-section" id="holdingsSection">
  <div class="section-header">
    <h2 class="section-heading">
      <i class="ri-vip-diamond-line heading-icon"></i>
      核心持仓
    </h2>
    <div class="section-meta">
      <span class="fund-count" id="holdingsCount">"""
        + str(len(held_funds))
        + """ 只基金</span>
    </div>
  </div>
  <div class="section-content" id="holdingsContent">"""
    )

    for code, data in held_funds.items():
        html += generate_fund_row_html(code, data, is_held=True)

    if not held_funds:
        html += '<div class="empty-state">暂无持仓基金</div>'

    html += "  </div>\n</section>"
    return html


def generate_watchlist_section_html(fund_map):
    """Generate Market Watchlist section with non-held funds"""
    watchlist_funds = {
        code: data for code, data in fund_map.items() if not data.get("is_hold", False)
    }

    html = (
        """<section class="content-section" id="watchlistSection">
  <div class="section-header">
    <h2 class="section-heading">
      <i class="ri-list-check-2 heading-icon"></i>
      市场观察
    </h2>
    <div class="section-meta">
      <span class="fund-count" id="watchlistCount">"""
        + str(len(watchlist_funds))
        + """ 只基金</span>
    </div>
  </div>
  <div class="section-content" id="watchlistContent">"""
    )

    for code, data in watchlist_funds.items():
        html += generate_fund_row_html(code, data, is_held=False)

    if not watchlist_funds:
        html += '<div class="empty-state">暂无观察基金</div>'

    html += "  </div>\n</section>"
    return html


def get_css_style():
    return r"""
    <link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet"/>
    <style>
        :root {
            /* Professional Trading Terminal Theme */
            --terminal-bg: #0b0e14;
            --card-bg: #151921;
            --border: #2d343f;
            --accent: #3b82f6;
            --text-main: #f1f5f9;
            --text-dim: #94a3b8;
            --text-muted: #64748b;
            --up: #ef4444;    /* 专业红 */
            --down: #10b981;  /* 专业绿 */
            --font-mono: 'JetBrains Mono', 'Courier New', Consolas, monospace;
            --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: var(--font-family);
            background-color: var(--terminal-bg);
            color: var(--text-main);
            line-height: 1.5;
            -webkit-font-smoothing: antialiased;
            min-height: 100vh;
        }

        /* ==================== TERMINAL DASHBOARD (资产看板) ==================== */
        .terminal-dashboard {
            display: grid;
            grid-template-columns: 1.5fr 1fr 1fr;
            gap: 20px;
            background: var(--card-bg);
            padding: 24px;
            border-radius: 12px;
            border: 1px solid var(--border);
            margin-bottom: 24px;
        }

        .stat-group label {
            color: var(--text-dim);
            font-size: 13px;
            display: block;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
        }

        .stat-group .big-num {
            font-family: var(--font-mono);
            font-size: 32px;
            font-weight: 700;
            line-height: 1.2;
            margin-bottom: 6px;
        }

        .stat-group .big-num.up {
            color: var(--up);
        }

        .stat-group .big-num.down {
            color: var(--down);
        }

        .stat-group .stat-change {
            font-size: 14px;
            font-family: var(--font-mono);
            color: var(--text-dim);
        }

        .stat-group .stat-change.up {
            color: var(--up);
        }

        .stat-group .stat-change.down {
            color: var(--down);
        }

        /* ==================== FUND GLASS CARDS (基金玻璃态卡片) ==================== */
        .holdings-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 16px;
            margin-top: 20px;
        }

        .fund-glass-card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            padding: 16px;
            border-radius: 10px;
            transition: all 0.2s ease;
            position: relative;
        }

        .fund-glass-card:hover {
            border-color: var(--accent);
            background: #1c222d;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
        }

        .card-title {
            font-weight: 600;
            font-size: 15px;
            color: var(--text-main);
            margin-bottom: 4px;
        }

        .card-code {
            color: var(--text-dim);
            font-family: var(--font-mono);
            font-size: 12px;
        }

        .card-code .tag {
            display: inline-block;
            background: rgba(59, 130, 246, 0.1);
            color: var(--accent);
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 11px;
            margin-left: 6px;
        }

        .card-badge {
            font-size: 20px;
            line-height: 1;
        }

        .card-main-data {
            display: flex;
            align-items: baseline;
            gap: 10px;
            margin: 10px 0;
        }

        .est-pct {
            font-family: var(--font-mono);
            font-size: 24px;
            font-weight: 700;
        }

        .est-pct.up {
            color: var(--up);
        }

        .est-pct.down {
            color: var(--down);
        }

        .card-details {
            display: grid;
            grid-template-columns: 1fr 1fr;
            border-top: 1px solid var(--border);
            padding-top: 12px;
            gap: 8px;
        }

        .detail-item {
            font-size: 12px;
            color: var(--text-dim);
        }

        .detail-item b {
            color: var(--text-main);
            font-family: var(--font-mono);
            display: block;
            font-size: 14px;
            margin-top: 4px;
        }

        .detail-item b.up {
            color: var(--up);
        }

        .detail-item b.down {
            color: var(--down);
        }

        /* Navbar */
        .navbar {
            background-color: var(--card-bg);
            color: var(--text-main);
            padding: 0.8rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
        }

        .navbar-brand {
            font-size: 1.25rem;
            font-weight: 600;
            letter-spacing: -0.02em;
            background: linear-gradient(135deg, var(--accent), var(--down));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            display: flex;
            align-items: center;
            flex: 0 0 auto;
        }

        .navbar-logo {
            width: 32px;
            height: 32px;
            margin-right: 0;
            vertical-align: middle;
            border-radius: 6px;
            object-fit: contain;
        }

        .navbar-quote {
            flex: 1;
            text-align: center;
            font-size: 1rem;
            font-weight: 500;
            color: var(--text-main);
            font-style: italic;
            padding: 0 2rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            letter-spacing: 0.05em;
        }

        .navbar-menu {
            display: flex;
            gap: 1rem;
            align-items: center;
        }

        .navbar-item {
            font-weight: 500;
            font-size: 0.9rem;
        }

        /* Layout */
        .app-container {
            display: flex;
            min-height: calc(100vh - 60px); /* Subtract navbar height */
            overflow: hidden; /* Prevent body scroll */
        }

        .tabs-header {
            display: flex;
            border-bottom: 2px solid var(--border);
            margin-bottom: 1rem;
            background: var(--card-bg);
            padding: 0 1rem;
        }

        .tab-button {
            padding: 12px 24px;
            background: none;
            border: none;
            cursor: pointer;
            font-weight: 500;
            text-align: center;
            position: relative;
            transition: all 0.2s;
            color: var(--text-dim);
            font-size: 0.9rem;
            border-bottom: 2px solid transparent;
        }

        .tab-button:hover {
            color: var(--text-main);
            background-color: var(--card-bg);
        }

        .tab-button.active {
            color: var(--text-main);
            border-bottom: 2px solid var(--accent);
        }

        .tab-content {
            display: none;
            padding: 1rem 0;
            animation: fadeIn 0.2s ease-in-out;
        }

        .tab-content.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(5px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .dashboard-grid {
            display: flex;
            flex-direction: column;
            gap: 2rem;
            max-width: 1200px;
            margin: 0 auto;
            padding-bottom: 40px;
        }

        .main-content {
            padding: 2rem;
            flex: 1;
            margin: 0;
            overflow-y: auto;
            height: calc(100vh - 60px);
            background-color: var(--terminal-bg);
        }

        /* Tables */
        .table-container {
            background: var(--card-bg);
            border: 1px solid var(--border);
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            margin-bottom: 1rem;
            border-radius: 12px;
        }

        .style-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }

        .style-table th {
            text-align: center;
            padding: 12px 16px;
            background-color: var(--card-bg);
            font-weight: 600;
            color: var(--text-main);
            border-bottom: 1px solid var(--border);
            white-space: nowrap;
            letter-spacing: 0.01em;
        }

        .style-table td {
            padding: 12px 16px;
            border-bottom: 1px solid var(--border);
            color: var(--text-main);
            font-weight: 400;
            text-align: center;
        }

        .style-table tbody tr:hover {
            background-color: var(--card-bg);
        }

        /* 最后一行的下划线加粗 */
        .style-table tbody tr:last-child td {
            border-bottom: 1px solid var(--border);
        }

        /* Sortable Headers */
        .style-table th.sortable {
            cursor: pointer;
            user-select: none;
            transition: color 0.2s;
        }

        .style-table th.sortable:hover {
            color: var(--accent);
        }

        .style-table th.sortable::after {
            content: '↕';
            display: inline-block;
            margin-left: 8px;
            font-size: 0.8em;
            color: var(--text-muted);
        }

        .style-table th.sorted-asc::after {
            content: '↑';
            color: var(--accent);
        }

        .style-table th.sorted-desc::after {
            content: '↓';
            color: var(--accent);
        }

        /* Numeric Columns Alignment & Font */
        .style-table th:nth-child(n+2),
        .style-table td:nth-child(n+2) {
            text-align: center;
            vertical-align: middle;
            font-family: var(--font-mono);
            font-variant-numeric: tabular-nums;
        }

        /* Sticky first column for mobile/tablet */
        @media (max-width: 1024px) {
            .style-table th:first-child,
            .style-table td:first-child {
                position: sticky;
                left: 0;
                background-color: var(--terminal-bg);
                z-index: 10;
                box-shadow: 2px 0 4px rgba(0,0,0,0.1);
            }

            .style-table th:first-child {
                z-index: 20;
                background-color: var(--card-bg);
            }

            .style-table tbody tr:hover td:first-child {
                background-color: var(--card-bg);
            }
        }

        /* Colors */
        .positive {
            color: var(--up) !important;
            font-weight: 600;
        }

        .negative {
            color: var(--down) !important;
            font-weight: 600;
        }
        
        /* Specific tweaks for small screens */
        @media (max-width: 768px) {
            body {
                font-size: 14px;
            }

            /* Navbar */
            .navbar {
                padding: 0.6rem 1rem;
                flex-wrap: wrap;
                gap: 0.5rem;
            }

            .navbar-brand {
                font-size: 1rem;
                flex: 0 0 auto;
                min-width: auto;
                display: flex;
                align-items: center;
            }

            .navbar-logo {
                width: 24px;
                height: 24px;
                margin-right: 0;
            }

            .navbar-quote {
                flex: 1;
                font-size: 0.75rem;
                font-weight: 500;
                padding: 0 0.5rem;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                text-align: center;
            }

            .navbar-menu {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                width: 100%;
                justify-content: flex-end;
            }

            .navbar-item {
                font-size: 0.75rem;
            }

            #toggle-chat-btn {
                font-size: 0.75rem !important;
                padding: 0 8px !important;
            }

            /* App container */
            .app-container {
                flex-direction: column;
                overflow: visible;
            }

            .main-content {
                height: auto;
                min-height: calc(100vh - 100px);
                padding: 1rem;
                overflow-y: visible;
            }

            .dashboard-grid {
                max-width: 100%;
                padding-bottom: 20px;
            }

            /* Tabs */
            .tabs-header {
                padding: 0;
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
                scrollbar-width: none;
            }

            .tabs-header::-webkit-scrollbar {
                display: none;
            }

            .tab-button {
                padding: 10px 12px;
                font-size: 0.8rem;
                white-space: nowrap;
                flex: 0 0 auto;
                min-width: 80px;
            }

            /* Tables - Enable horizontal scroll */
            .table-container {
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
                border-radius: 0;
            }

            .style-table {
                font-size: 0.75rem;
                min-width: 100%;
            }

            .style-table th {
                padding: 8px 10px;
                font-size: 0.75rem;
                white-space: nowrap;
            }

            .style-table td {
                padding: 8px 10px;
                font-size: 0.75rem;
            }

            /* Make numeric columns more compact on mobile */
            .style-table th:nth-child(n+4),
            .style-table td:nth-child(n+4) {
                padding: 8px 6px;
                font-size: 0.7rem;
            }

            /* Hide less important columns on very small screens */
            @media (max-width: 480px) {
                .style-table td:nth-child(n+7),
                .style-table th:nth-child(n+7) {
                    display: none;
                }
            }

            /* Loading page adjustments */
            .loading-container {
                padding: 1rem;
            }

            .task-list {
                max-width: 100%;
            }

            .task-item {
                font-size: 0.85rem;
            }
        }

        /* Fund Operations Panel */
        .fund-operations {
            position: sticky;
            top: 0;
            background: var(--card-bg);
            backdrop-filter: blur(10px);
            padding: 16px;
            border-radius: 12px;
            box-shadow: 0 4px 16px rgba(102, 126, 234, 0.15);
            margin-bottom: 20px;
            z-index: 100;
            border: 1px solid var(--border);
        }

        .operation-group {
            display: flex;
            gap: 12px;
            align-items: center;
            margin-bottom: 12px;
            flex-wrap: wrap;
        }

        .operation-group:last-child {
            margin-bottom: 0;
        }

        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            color: white;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            border: 1px solid transparent;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        }

        .btn:active {
            transform: translateY(0);
        }

        .btn-primary {
            background: var(--accent);
            border-color: var(--accent);
        }

        .btn-primary:hover {
            background: var(--accent);
            border-color: var(--accent);
        }

        .btn-success {
            color: #ffffff;
            background-color: var(--down);
            border-color: var(--down);
        }

        .btn-success:hover {
            background-color: #059669;
            border-color: #059669;
        }

        .btn-warning {
            color: #ffffff;
            background-color: #f59e0b;
            border-color: #f59e0b;
        }

        .btn-warning:hover {
            background-color: #d97706;
            border-color: #d97706;
        }

        .btn-info {
            color: #ffffff;
            background: var(--accent);
            border-color: var(--accent);
        }

        .btn-info:hover {
            background: var(--accent);
            border-color: var(--accent);
        }

        .btn-danger {
            color: #ffffff;
            background-color: var(--up);
            border-color: var(--up);
        }

        .btn-danger:hover {
            background-color: #dc2626;
            border-color: #dc2626;
        }

        .btn-secondary {
            color: #ffffff;
            background-color: #6b7280;
            border-color: #6b7280;
        }

        .btn-secondary:hover {
            background-color: #4b5563;
            border-color: #4b5563;
        }

        /* 份额按钮样式 */
        .shares-button {
            padding: 6px 12px;
            background: #3b82f6;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.2s;
        }

        .shares-button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        }

        .shares-button:active {
            transform: translateY(0);
        }

        #fundCodesInput {
            flex: 1;
            min-width: 250px;
            padding: 8px 12px;
            border: 1px solid var(--border);
            border-radius: 6px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s, box-shadow 0.2s;
            color: var(--text-main);
            background-color: var(--terminal-bg);
        }

        #fundCodesInput:focus {
            border-color: var(--accent);
            box-shadow: 0 0 0 3px rgba(9, 105, 218, 0.3);
        }

        #fundCodesInput::placeholder {
            color: var(--text-muted);
        }

        .selected-info {
            margin-left: auto;
            color: var(--text-dim);
            font-size: 14px;
        }

        .selected-info strong {
            color: var(--accent);
            font-size: 16px;
        }

        /* Checkbox styling */
        .fund-checkbox {
            width: 18px;
            height: 18px;
            cursor: pointer;
            accent-color: var(--accent);
        }

        #selectAll {
            width: 18px;
            height: 18px;
            cursor: pointer;
            accent-color: var(--accent);
        }

        /* Sector Modal */
        .sector-modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }

        .sector-modal.active {
            display: flex;
        }

        .sector-modal-content {
            background: var(--terminal-bg);
            padding: 24px;
            border: 1px solid var(--border);
            border-radius: 6px;
            width: 90%;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
        }

        .sector-modal-header {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 20px;
            color: var(--text-main);
        }

        .sector-modal-search {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid var(--border);
            border-radius: 6px;
            margin-bottom: 16px;
            font-size: 14px;
            color: var(--text-main);
            background-color: var(--terminal-bg);
        }

        .sector-modal-search:focus {
            border-color: var(--accent);
            outline: none;
            box-shadow: 0 0 0 3px rgba(9, 105, 218, 0.3);
        }

        .sector-category {
            margin-bottom: 16px;
        }

        .sector-category-header {
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 8px;
            color: var(--accent);
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .sector-category-header:hover {
            text-decoration: underline;
        }

        .sector-items {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            gap: 8px;
        }

        .sector-item {
            padding: 8px 12px;
            border: 1px solid var(--border);
            border-radius: 6px;
            cursor: pointer;
            text-align: center;
            transition: all 0.2s;
            font-size: 13px;
            color: var(--text-main);
            background-color: var(--terminal-bg);
        }

        .sector-item:hover {
            background-color: var(--card-bg);
            border-color: var(--accent);
        }

        .sector-item.selected {
            background-color: var(--accent);
            color: white;
            border-color: var(--accent);
        }

        .sector-modal-footer {
            display: flex;
            gap: 12px;
            justify-content: flex-end;
            margin-top: 20px;
        }

        /* Floating Action Bar */
        .floating-action-bar {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--terminal-bg);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 12px 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            display: none;
            z-index: 100;
            gap: 8px;
            align-items: center;
        }

        .floating-action-bar.visible {
            display: flex;
        }

        /* Add Fund Input */
        .add-fund-input {
            display: flex;
            gap: 12px;
            align-items: center;
            margin-bottom: 20px;
            padding: 16px;
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 6px;
        }

        /* Confirm Dialog */
        .confirm-dialog {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }

        .confirm-dialog.active {
            display: flex;
        }

        .confirm-dialog-content {
            background: var(--terminal-bg);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 24px;
            max-width: 400px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
        }

        .confirm-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 12px;
            color: var(--text-main);
        }

        .confirm-message {
            font-size: 14px;
            color: var(--text-dim);
            margin-bottom: 20px;
            line-height: 1.5;
        }

        .confirm-actions {
            display: flex;
            gap: 12px;
            justify-content: flex-end;
        }

        /* Responsive adjustments */
        @media (max-width: 768px) {
            .floating-action-bar {
                flex-wrap: wrap;
                bottom: 10px;
                left: 10px;
                right: 10px;
                transform: none;
            }

            .add-fund-input {
                flex-direction: column;
                align-items: stretch;
            }

            .btn {
                justify-content: center;
            }

            #fundCodesInput {
                min-width: 100%;
            }

            .selected-info {
                margin-left: 0;
                text-align: center;
            }
        }
    </style>
    """


def get_javascript_code():
    return r"""
    <!-- Import Map for ESM modules -->
    <script>
    // Polyfill process for React libraries
    window.process = {
        env: {
            NODE_ENV: 'production'
        }
    };
    window.onerror = function(message, source, lineno, colno, error) {
        console.error("Global Error Caught:", error);
        const root = document.getElementById('pro-chat-root');
        if (root && root.innerHTML === '') {
            root.innerHTML = `<div style="padding:20px; color:red;">
                <h3>Failed to load Pro Chat</h3>
                <p>Error: ${message}</p>
                <p>Dependencies might be missing in CDN mode.</p>
                <button onclick="location.reload()" style="padding:5px 10px; margin-top:10px;">Retry</button>
            </div>`;
        }
    };
    </script>
    <link rel="stylesheet" href="https://unpkg.com/quikchat/dist/quikchat.css">
    <script src="https://unpkg.com/quikchat"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

    <script>
    document.addEventListener('DOMContentLoaded', function() {
        // Initialize Auto Colorize
        autoColorize();

        // 🔧 独立的对话历史管理 - 不依赖 QuikChat 内部状态
        let conversationHistory = [];

        // Initialize QuikChat
        const chat = new quikchat('#pro-chat-root', async (instance, message) => {
            // Display user message immediately
            instance.messageAddNew(message, 'You', 'right');
            
            // 🔧 添加用户消息到独立历史
            conversationHistory.push({
                role: 'user',
                content: message
            });
            
            console.log("💬 Current conversation history:", conversationHistory);
            
            // 不再收集前端context，所有数据由后端获取
            console.log("Sending message to backend (context will be fetched by backend)");

            // Create loading indicator
            const loadingHtml = '<div class="ai-loading-indicator" style="display: flex; align-items: center; gap: 10px;"><div class="typing-indicator"><span></span><span></span><span></span></div><span style="color: #999;">AI Analyst is thinking...</span></div>';
            instance.messageAddNew(loadingHtml, 'System', 'left');

            try {
                let streamingContent = '';
                let hasReceivedContent = false;
                let contentDisplayed = false;
                let loadingRemoved = false;
                let currentStepElement = null; // Track current step status element
                
                // Helper to remove loading indicator
                function removeLoadingIndicator() {
                    if (!loadingRemoved) {
                        try {
                            // Find and remove by class name
                            const loadingElements = document.querySelectorAll('.ai-loading-indicator');
                            loadingElements.forEach(el => {
                                const messageDiv = el.closest('.quikchat-message');
                                if (messageDiv) {
                                    messageDiv.remove();
                                }
                            });
                            loadingRemoved = true;
                            console.log('Loading indicator removed');
                        } catch (e) {
                            console.warn('Failed to remove loading indicator:', e);
                        }
                    }
                }
                
                // Helper to show step status
                function showStepStatus(message, icon = '⏳') {
                    // Remove previous step if exists
                    if (currentStepElement) {
                        try {
                            currentStepElement.remove();
                            console.log('Previous step removed');
                        } catch (e) {
                            console.warn('Failed to remove previous step:', e);
                        }
                    }
                    
                    // Create new step status
                    const stepHtml = `<div style="display: flex; align-items: center; gap: 8px; padding: 4px 8px; background: rgba(13,138,188,0.1); border-radius: 4px;">
                        <span style="font-size: 1.2em;">${icon}</span>
                        <span style="color: #42a5f5; font-size: 0.9em;">${message}</span>
                    </div>`;
                    
                    instance.messageAddNew(stepHtml, 'System', 'left');
                    
                    // Get the newly added element
                    setTimeout(() => {
                        const allMessages = document.querySelectorAll('.quikchat-message');
                        currentStepElement = allMessages[allMessages.length - 1];
                    }, 10);
                }
                
                // Use fetch with SSE
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        message: message,
                        history: conversationHistory.slice(0, -1)  // 🔧 使用独立历史，排除刚添加的当前消息
                    })
                });

                if (!response.ok) {
                    instance.messageAddNew('Network Error: ' + response.statusText, 'System', 'left');
                    return;
                }

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';
                let lastChunkTime = Date.now();
                
                // Timeout checker
                const timeoutChecker = setInterval(() => {
                    const timeSinceLastChunk = Date.now() - lastChunkTime;
                    if (timeSinceLastChunk > 30000) { // 30 seconds timeout
                        console.warn('Stream timeout detected');
                        clearInterval(timeoutChecker);
                        reader.cancel();
                    }
                }, 5000);
                
                // Helper function to detect and render content
                function renderContent(content) {
                    const looksLikeHTML = content.trim().startsWith('<') && /<[^>]+>/.test(content);
                    if (looksLikeHTML) {
                        return content;
                    } else {
                        try {
                            if (typeof marked !== 'undefined') {
                                return marked.parse(content);
                            }
                        } catch (e) {
                            console.warn('Marked.js not available or parsing failed:', e);
                        }
                        return content;
                    }
                }
                
                // Helper function to display content with typewriter effect
                function displayWithTypewriter(content) {
                    if (contentDisplayed) return; // Prevent duplicate display
                    contentDisplayed = true;
                    
                    // 🔧 重要：将AI的真实回复保存到独立历史中
                    conversationHistory.push({
                        role: 'assistant',
                        content: content  // 保存原始内容（HTML格式）
                    });
                    console.log('✅ AI response saved to conversation history');
                    console.log('💬 Updated conversation history:', conversationHistory);
                    
                    const uniqueId = 'typewriter-' + Date.now();
                    instance.messageAddNew(`<div id="${uniqueId}"></div>`, 'AI Analyst', 'left');
                    
                    setTimeout(() => {
                        const typewriterDiv = document.getElementById(uniqueId);
                        if (typewriterDiv) {
                            const contentLength = content.length;
                            let currentIndex = 0;
                            
                            let speed, interval;
                            if (contentLength < 500) {
                                speed = 15;
                                interval = 20;
                            } else if (contentLength < 2000) {
                                speed = 30;
                                interval = 15;
                            } else {
                                speed = 50;
                                interval = 10;
                            }
                            
                            console.log(`Typewriter: ${contentLength} chars, speed=${speed}, interval=${interval}ms`);

                            const typewriterInterval = setInterval(() => {
                                if (currentIndex < contentLength) {
                                    currentIndex += speed;
                                    typewriterDiv.textContent = content.substring(0, Math.min(currentIndex, contentLength));

                                    // Auto-scroll to keep the message visible
                                    typewriterDiv.scrollIntoView({ behavior: 'smooth', block: 'end' });
                                } else {
                                    const renderedContent = renderContent(content);
                                    typewriterDiv.innerHTML = renderedContent;
                                    typewriterDiv.removeAttribute('id');
                                    clearInterval(typewriterInterval);

                                    // Final scroll to ensure full content is visible
                                    typewriterDiv.scrollIntoView({ behavior: 'smooth', block: 'end' });
                                    console.log('Content rendered');
                                }
                            }, interval);
                        }
                    }, 50);
                }
                
                while (true) {
                    const { done, value } = await reader.read();
                    
                    if (done) {
                        clearInterval(timeoutChecker);
                        break;
                    }
                    
                    lastChunkTime = Date.now();
                    buffer += decoder.decode(value, { stream: true });
                    
                    // Process SSE messages
                    const lines = buffer.split('\n');
                    buffer = lines.pop(); // Keep incomplete line in buffer
                    
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.substring(6));
                                
                                if (data.type === 'status') {
                                    // Remove initial loading indicator on first status
                                    removeLoadingIndicator();
                                    
                                    // Show step status with animated icon
                                    showStepStatus(data.message, '⏳');
                                    console.log('Status:', data.message);
                                } else if (data.type === 'tool_call') {
                                    // Show tool call step
                                    const toolNames = data.tools.join(', ');
                                    showStepStatus(`正在调用: ${toolNames}`, '🔍');
                                    console.log('Calling tools:', data.tools);
                                } else if (data.type === 'content') {
                                    // Remove all status indicators when content starts
                                    removeLoadingIndicator();
                                    if (currentStepElement) {
                                        currentStepElement.remove();
                                        currentStepElement = null;
                                    }
                                    console.log('All indicators removed, starting content');
                                    
                                    streamingContent += data.chunk;
                                    hasReceivedContent = true;
                                } else if (data.type === 'done') {
                                    console.log('Streaming complete, total length:', streamingContent.length);
                                    // Remove any remaining step indicators
                                    if (currentStepElement) {
                                        currentStepElement.remove();
                                        currentStepElement = null;
                                    }
                                    if (streamingContent) {
                                        displayWithTypewriter(streamingContent);
                                    }
                                } else if (data.type === 'error' || data.error) {
                                    // Remove step indicators on error
                                    if (currentStepElement) {
                                        currentStepElement.remove();
                                        currentStepElement = null;
                                    }
                                    instance.messageAddNew('Error: ' + (data.message || data.error), 'System', 'left');
                                }
                            } catch (e) {
                                console.error('Failed to parse SSE data:', e, 'Line:', line);
                            }
                        }
                    }
                }

                // Fallback: if we received content but no 'done' signal, display it anyway
                if (hasReceivedContent && streamingContent && !contentDisplayed) {
                    console.warn('Stream ended without done signal, displaying partial content');
                    displayWithTypewriter(streamingContent);
                } else if (!streamingContent && !contentDisplayed) {
                    instance.messageAddNew('No response received.', 'System', 'left');
                }

            } catch (err) {
                console.error('Chat error:', err);
                instance.messageAddNew('Network Error: ' + err.message, 'System', 'left');
            }
        }, {
            theme: 'quikchat-theme-dark',
            botName: 'AI Analyst',
            userAvatar: 'https://ui-avatars.com/api/?name=User&background=0D8ABC&color=fff',
            botAvatar: 'https://ui-avatars.com/api/?name=AI&background=ff9900&color=fff',
            placeholder: 'Ask about market data...'
        });

        // Add welcome message
        setTimeout(() => {
            const welcomeMsg = "Welcome to LanFund Pro Terminal. Connected to market data stream.";
            chat.messageAddNew(welcomeMsg, 'System', 'left');
            
            // 🔧 将欢迎消息也添加到历史中（作为 assistant 消息）
            conversationHistory.push({
                role: 'assistant',
                content: welcomeMsg
            });
            console.log('💬 Initialized conversation history with welcome message');
        }, 500);

        // Initialize resize functionality
        const resizeHandle = document.getElementById('resize-handle');
        const chatSidebar = document.getElementById('chat-sidebar');
        let isResizing = false;
        let startX = 0;
        let startWidth = 0;

        resizeHandle.addEventListener('mousedown', function(e) {
            isResizing = true;
            startX = e.clientX;
            startWidth = chatSidebar.offsetWidth;
            resizeHandle.classList.add('resizing');
            document.body.style.cursor = 'ew-resize';
            document.body.style.userSelect = 'none';
            e.preventDefault();
        });

        document.addEventListener('mousemove', function(e) {
            if (!isResizing) return;
            
            const dx = startX - e.clientX; // Reversed because we're dragging from the left
            const newWidth = startWidth + dx;
            
            // Constrain width between min and max
            const minWidth = 300;
            const maxWidth = 800;
            const constrainedWidth = Math.min(Math.max(newWidth, minWidth), maxWidth);
            
            chatSidebar.style.width = constrainedWidth + 'px';
        });

        document.addEventListener('mouseup', function() {
            if (isResizing) {
                isResizing = false;
                resizeHandle.classList.remove('resizing');
                document.body.style.cursor = '';
                document.body.style.userSelect = '';
            }
        });
    });

    // Toggle chat sidebar function
    function toggleChatSidebar() {
        const chatSidebar = document.getElementById('chat-sidebar');
        const toggleIcon = document.getElementById('chat-toggle-icon');

        if (chatSidebar.classList.contains('hidden')) {
            chatSidebar.classList.remove('hidden');
            toggleIcon.textContent = '◀';
        } else {
            chatSidebar.classList.add('hidden');
            toggleIcon.textContent = '▶';
        }
    }
    </script>


    <!-- Standard JS for table coloring -->
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        autoColorize();
    });

    function autoColorize() {
        const cells = document.querySelectorAll('.style-table td');
        cells.forEach(cell => {
            const text = cell.textContent.trim();
            const cleanText = text.replace(/[%,亿万手]/g, '');
            const val = parseFloat(cleanText);

            if (!isNaN(val)) {
                if (text.includes('%') || text.includes('涨跌')) {
                    if (text.includes('-')) {
                        cell.classList.add('negative');
                    } else if (val > 0) {
                        cell.classList.add('positive');
                    }
                } else if (text.startsWith('-')) {
                    cell.classList.add('negative');
                } else if (text.startsWith('+')) {
                    cell.classList.add('positive');
                }
            }
        });
    }

    function sortTable(table, columnIndex) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const currentSortCol = table.dataset.sortCol;
        const currentSortDir = table.dataset.sortDir || 'asc';
        let direction = 'asc';

        if (currentSortCol == columnIndex) {
            direction = currentSortDir === 'asc' ? 'desc' : 'asc';
        }
        table.dataset.sortCol = columnIndex;
        table.dataset.sortDir = direction;

        rows.sort((a, b) => {
            const aText = a.cells[columnIndex].textContent.trim();
            const bText = b.cells[columnIndex].textContent.trim();
            const valA = parseValue(aText);
            const valB = parseValue(bText);
            let comparison = 0;
            if (valA > valB) {
                comparison = 1;
            } else if (valA < valB) {
                comparison = -1;
            }
            return direction === 'asc' ? comparison : -comparison;
        });

        tbody.innerHTML = '';
        rows.forEach(row => tbody.appendChild(row));

        table.querySelectorAll('th').forEach(th => {
            th.classList.remove('sorted-asc', 'sorted-desc');
        });
        const headerToUpdate = table.querySelectorAll('th')[columnIndex];
        if (headerToUpdate) {
            headerToUpdate.classList.add(direction === 'asc' ? 'sorted-asc' : 'sorted-desc');
        }
    }

    function parseValue(val) {
        if (val === 'N/A' || val === '--' || val === '---' || val === '') {
            return -Infinity;
        }
        const cleanedVal = val.replace(/%|亿|万|元\/克|手/g, '').replace(/,/g, '');
        const num = parseFloat(cleanedVal);
        return isNaN(num) ? val.toLowerCase() : num;
    }

    function openTab(evt, tabId) {
        // Hide all tab contents
        const allContents = document.querySelectorAll('.tab-content');
        allContents.forEach(content => {
            content.classList.remove('active');
        });

        // Remove active class from all tab buttons
        const allButtons = document.querySelectorAll('.tab-button');
        allButtons.forEach(button => {
            button.classList.remove('active');
        });

        // Show the clicked tab's content and add active class to the button
        document.getElementById(tabId).classList.add('active');
        evt.currentTarget.classList.add('active');
    }

    // Fund Operations Functions
    // 板块分类数据
    const SECTOR_CATEGORIES = {
        "科技": ["人工智能", "半导体", "云计算", "5G", "光模块", "CPO", "F5G", "通信设备", "PCB", "消费电子",
                "计算机", "软件开发", "信创", "网络安全", "IT服务", "国产软件", "计算机设备", "光通信",
                "算力", "脑机接口", "通信", "电子", "光学光电子", "元件", "存储芯片", "第三代半导体",
                "光刻胶", "电子化学品", "LED", "毫米波", "智能穿戴", "东数西算", "数据要素", "国资云",
                "Web3.0", "AIGC", "AI应用", "AI手机", "AI眼镜", "DeepSeek", "TMT", "科技"],
        "医药健康": ["医药生物", "医疗器械", "生物疫苗", "CRO", "创新药", "精准医疗", "医疗服务", "中药",
                    "化学制药", "生物制品", "基因测序", "超级真菌"],
        "消费": ["食品饮料", "白酒", "家用电器", "纺织服饰", "商贸零售", "新零售", "家居用品", "文娱用品",
                "婴童", "养老产业", "体育", "教育", "在线教育", "社会服务", "轻工制造", "新消费",
                "可选消费", "消费", "家电零部件", "智能家居"],
        "金融": ["银行", "证券", "保险", "非银金融", "国有大型银行", "股份制银行", "城商行", "金融"],
        "能源": ["新能源", "煤炭", "石油石化", "电力", "绿色电力", "氢能源", "储能", "锂电池", "电池",
                "光伏设备", "风电设备", "充电桩", "固态电池", "能源", "煤炭开采", "公用事业", "锂矿"],
        "工业制造": ["机械设备", "汽车", "新能源车", "工程机械", "高端装备", "电力设备", "专用设备",
                    "通用设备", "自动化设备", "机器人", "人形机器人", "汽车零部件", "汽车服务",
                    "汽车热管理", "尾气治理", "特斯拉", "无人驾驶", "智能驾驶", "电网设备", "电机",
                    "高端制造", "工业4.0", "工业互联", "低空经济", "通用航空"],
        "材料": ["有色金属", "黄金股", "贵金属", "基础化工", "钢铁", "建筑材料", "稀土永磁", "小金属",
                "工业金属", "材料", "大宗商品", "资源"],
        "军工": ["国防军工", "航天装备", "航空装备", "航海装备", "军工电子", "军民融合", "商业航天",
                "卫星互联网", "航母", "航空机场"],
        "基建地产": ["建筑装饰", "房地产", "房地产开发", "房地产服务", "交通运输", "物流"],
        "环保": ["环保", "环保设备", "环境治理", "垃圾分类", "碳中和", "可控核聚变", "液冷"],
        "传媒": ["传媒", "游戏", "影视", "元宇宙", "超清视频", "数字孪生"],
        "主题": ["国企改革", "一带一路", "中特估", "中字头", "并购重组", "华为", "新兴产业",
                "国家安防", "安全主题", "农牧主题", "农林牧渔", "养殖业", "猪肉", "高端装备"]
    };

    // 基金选择模态框相关变量
    let currentOperation = null;
    let selectedFundsForOperation = [];
    let allFunds = [];

    // 打开基金选择模态框
    async function openFundSelectionModal(operation) {
        currentOperation = operation;
        selectedFundsForOperation = [];

        // 设置标题
        const titles = {
            'hold': '选择要标记持有的基金',
            'unhold': '选择要取消持有的基金',
            'sector': '选择要标注板块的基金',
            'unsector': '选择要删除板块的基金',
            'delete': '选择要删除的基金'
        };
        document.getElementById('fundSelectionTitle').textContent = titles[operation] || '选择基金';

        // 获取所有基金列表
        try {
            const response = await fetch('/api/fund/data');
            const fundMap = await response.json();
            allFunds = Object.entries(fundMap).map(([code, data]) => ({
                code,
                name: data.fund_name,
                is_hold: data.is_hold,
                sectors: data.sectors || []
            }));

            // 渲染基金列表
            renderFundSelectionList(allFunds);

            // 显示模态框
            document.getElementById('fundSelectionModal').classList.add('active');
        } catch (e) {
            alert('获取基金列表失败: ' + e.message);
        }
    }

    // 渲染基金选择列表
    function renderFundSelectionList(funds) {
        const listContainer = document.getElementById('fundSelectionList');

        // HTML escape function to prevent XSS and syntax errors
        const escapeHtml = (text) => {
            if (!text) return '';
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        };

        // Escape fund code for use in onclick attribute
        const escapeJs = (text) => {
            if (!text) return '';
            return text.replace(/\\/g, '\\\\').replace(/'/g, "\\'");
        };

        listContainer.innerHTML = funds.map(fund => {
            const safeCode = escapeHtml(String(fund.code));
            const safeName = escapeHtml(String(fund.name));
            const safeCodeForJs = escapeJs(String(fund.code));
            const safeSectors = fund.sectors && fund.sectors.length > 0
                ? escapeHtml(fund.sectors.join(', '))
                : '';

            return `
            <div class="sector-item" style="text-align: left; padding: 12px; margin-bottom: 8px; cursor: pointer; display: flex; align-items: center; gap: 10px;"
                 onclick="toggleFundSelection('${safeCodeForJs}', this)">
                <input type="checkbox" class="fund-selection-checkbox" data-code="${safeCode}"
                       style="width: 18px; height: 18px; cursor: pointer;" onclick="event.stopPropagation();">
                <div style="flex: 1;">
                    <div style="font-weight: 600;">${safeCode} - ${safeName}</div>
                    ${fund.is_hold ? '<span style="color: #3b82f6; font-size: 12px;">⭐ 持有</span>' : ''}
                    ${safeSectors ? `<span style="color: #8b949e; font-size: 12px;"> 🏷️ ${safeSectors}</span>` : ''}
                </div>
            </div>
            `;
        }).join('');
    }

    // 切换基金选择状态
    function toggleFundSelection(code, element) {
        const checkbox = element.querySelector('.fund-selection-checkbox');
        checkbox.checked = !checkbox.checked;

        if (checkbox.checked) {
            if (!selectedFundsForOperation.includes(code)) {
                selectedFundsForOperation.push(code);
            }
            element.style.backgroundColor = 'rgba(102, 126, 234, 0.2)';
        } else {
            selectedFundsForOperation = selectedFundsForOperation.filter(c => c !== code);
            element.style.backgroundColor = '';
        }
    }

    // 关闭基金选择模态框
    function closeFundSelectionModal() {
        document.getElementById('fundSelectionModal').classList.remove('active');
        currentOperation = null;
        selectedFundsForOperation = [];
    }

    // 确认基金选择
    async function confirmFundSelection() {
        if (selectedFundsForOperation.length === 0) {
            alert('请至少选择一个基金');
            return;
        }

        // 根据操作类型执行相应的操作
        switch (currentOperation) {
            case 'hold':
                await markHold(selectedFundsForOperation);
                break;
            case 'unhold':
                await unmarkHold(selectedFundsForOperation);
                break;
            case 'sector':
                closeFundSelectionModal();
                openSectorModal(selectedFundsForOperation);
                return; // 不关闭，等待板块选择
            case 'unsector':
                await removeSector(selectedFundsForOperation);
                break;
            case 'delete':
                await deleteFunds(selectedFundsForOperation);
                break;
        }

        closeFundSelectionModal();
    }

    // 基金选择搜索
    document.addEventListener('DOMContentLoaded', function() {
        const searchInput = document.getElementById('fundSelectionSearch');
        if (searchInput) {
            searchInput.addEventListener('input', function() {
                const keyword = this.value.toLowerCase();
                const filtered = allFunds.filter(fund =>
                    fund.code.includes(keyword) || fund.name.toLowerCase().includes(keyword)
                );
                renderFundSelectionList(filtered);
            });
        }
    });

    // 确认对话框相关函数
    let confirmCallback = null;

    function showConfirmDialog(title, message, onConfirm) {
        document.getElementById('confirmTitle').textContent = title;
        document.getElementById('confirmMessage').textContent = message;
        document.getElementById('confirmDialog').classList.add('active');
        confirmCallback = onConfirm;
    }

    function closeConfirmDialog() {
        document.getElementById('confirmDialog').classList.remove('active');
        confirmCallback = null;
    }

    document.getElementById('confirmBtn').addEventListener('click', function() {
        if (confirmCallback) {
            confirmCallback();
        }
        closeConfirmDialog();
    });

    // 添加基金
    async function addFunds() {
        const input = document.getElementById('fundCodesInput');
        const codes = input.value.trim();
        if (!codes) {
            alert('请输入基金代码');
            return;
        }

        try {
            const response = await fetch('/api/fund/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ codes })
            });
            const result = await response.json();
            if (result.success) {
                alert(result.message);
                location.reload();
            } else {
                alert(result.message);
            }
        } catch (e) {
            alert('操作失败: ' + e.message);
        }
    }

    // 删除基金
    async function deleteFunds(codes) {
        showConfirmDialog(
            '删除基金',
            `确定要删除 ${codes.length} 只基金吗？`,
            async () => {
                try {
                    const response = await fetch('/api/fund/delete', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ codes: codes.join(',') })
                    });
                    const result = await response.json();
                    if (result.success) {
                        alert(result.message);
                        location.reload();
                    } else {
                        alert(result.message);
                    }
                } catch (e) {
                    alert('操作失败: ' + e.message);
                }
            }
        );
    }

    // 标记持有
    async function markHold(codes) {
        showConfirmDialog(
            '标记持有',
            `确定要标记 ${codes.length} 只基金为持有吗？`,
            async () => {
                try {
                    const response = await fetch('/api/fund/hold', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ codes: codes.join(','), hold: true })
                    });
                    const result = await response.json();
                    if (result.success) {
                        alert(result.message);
                        location.reload();
                    } else {
                        alert(result.message);
                    }
                } catch (e) {
                    alert('操作失败: ' + e.message);
                }
            }
        );
    }

    // 取消持有
    async function unmarkHold(codes) {
        showConfirmDialog(
            '取消持有',
            `确定要取消 ${codes.length} 只基金的持有标记吗？`,
            async () => {
                try {
                    const response = await fetch('/api/fund/hold', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ codes: codes.join(','), hold: false })
                    });
                    const result = await response.json();
                    if (result.success) {
                        alert(result.message);
                        location.reload();
                    } else {
                        alert(result.message);
                    }
                } catch (e) {
                    alert('操作失败: ' + e.message);
                }
            }
        );
    }

    // 打开板块选择模态框（用于标注板块）
    let selectedCodesForSector = [];

    function openSectorModal(codes) {
        selectedCodesForSector = codes;
        document.getElementById('sectorModal').classList.add('active');
        renderSectorCategories();
    }

    // 删除板块标记
    async function removeSector(codes) {
        showConfirmDialog(
            '删除板块标记',
            `确定要删除 ${codes.length} 只基金的板块标记吗？`,
            async () => {
                try {
                    const response = await fetch('/api/fund/sector/remove', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ codes: codes.join(',') })
                    });
                    const result = await response.json();
                    if (result.success) {
                        alert(result.message);
                        location.reload();
                    } else {
                        alert(result.message);
                    }
                } catch (e) {
                    alert('操作失败: ' + e.message);
                }
            }
        );
    }

    // 取消持有
    async function unmarkHold() {
        const codes = getSelectedCodes();
        if (codes.length === 0) {
            alert('请先选择要取消持有的基金');
            return;
        }

        showConfirmDialog(
            '取消持有',
            `确定要取消 ${codes.length} 只基金的持有标记吗？`,
            async () => {
                try {
                    const response = await fetch('/api/fund/hold', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ codes: codes.join(','), hold: false })
                    });
                    const result = await response.json();
                    if (result.success) {
                        alert(result.message);
                        location.reload();
                    } else {
                        alert(result.message);
                    }
                } catch (e) {
                    alert('操作失败: ' + e.message);
                }
            }
        );
    }

    // 板块选择相关
    let selectedSectors = [];

    function renderSectorCategories() {
        // 生成板块分类HTML
        const container = document.getElementById('sectorCategories');
        container.innerHTML = '';

        for (const [category, sectors] of Object.entries(SECTOR_CATEGORIES)) {
            const categoryDiv = document.createElement('div');
            categoryDiv.className = 'sector-category';

            const header = document.createElement('div');
            header.className = 'sector-category-header';
            header.innerHTML = `<span>${category}</span><span>▼</span>`;
            header.onclick = () => {
                const items = categoryDiv.querySelector('.sector-items');
                items.style.display = items.style.display === 'none' ? 'grid' : 'none';
            };

            const itemsDiv = document.createElement('div');
            itemsDiv.className = 'sector-items';

            sectors.forEach(sector => {
                const item = document.createElement('div');
                item.className = 'sector-item';
                item.textContent = sector;
                item.onclick = () => {
                    item.classList.toggle('selected');
                    if (item.classList.contains('selected')) {
                        if (!selectedSectors.includes(sector)) {
                            selectedSectors.push(sector);
                        }
                    } else {
                        selectedSectors = selectedSectors.filter(s => s !== sector);
                    }
                };
                itemsDiv.appendChild(item);
            });

            categoryDiv.appendChild(header);
            categoryDiv.appendChild(itemsDiv);
            container.appendChild(categoryDiv);
        }

        selectedSectors = [];
        document.getElementById('sectorModal').classList.add('active');
    }

    function closeSectorModal() {
        document.getElementById('sectorModal').classList.remove('active');
        selectedSectors = [];
    }

    async function confirmSector() {
        if (selectedSectors.length === 0) {
            alert('请至少选择一个板块');
            return;
        }

        try {
            const response = await fetch('/api/fund/sector', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ codes: selectedCodesForSector.join(','), sectors: selectedSectors })
            });
            const result = await response.json();
            closeSectorModal();
            if (result.success) {
                alert(result.message);
                location.reload();
            } else {
                alert(result.message);
            }
        } catch (e) {
            closeSectorModal();
            alert('操作失败: ' + e.message);
        }
    }

    // ==================== 新增功能：份额管理和文件操作 ====================

    // 当前正在编辑份额的基金代码
    let currentSharesFundCode = null;

    // 获取基金份额（从内存或DOM）- 必须在 openSharesModal 之前定义
    window.getFundShares = function(fundCode) {
        // 先从全局存储获取
        if (window.fundSharesData && window.fundSharesData[fundCode]) {
            return window.fundSharesData[fundCode];
        }
        return 0;
    };

    // 更新份额按钮状态 - 必须在 openSharesModal 之前定义
    function updateSharesButton(fundCode, shares) {
        const button = document.getElementById('sharesBtn_' + fundCode);
        if (button) {
            if (shares > 0) {
                button.textContent = '修改';
                button.style.background = '#10b981';
            } else {
                button.textContent = '设置';
                button.style.background = '#3b82f6';
            }
        }
    }

    // 打开份额设置弹窗
    window.openSharesModal = function(fundCode) {
        currentSharesFundCode = fundCode;
        const modal = document.getElementById('sharesModal');
        const fundCodeDisplay = document.getElementById('sharesModalFundCode');
        const sharesInput = document.getElementById('sharesModalInput');

        // 获取当前份额
        const sharesValue = window.getFundShares(fundCode) || 0;
        sharesInput.value = sharesValue > 0 ? sharesValue : '';
        fundCodeDisplay.textContent = fundCode;

        // 更新弹窗标题
        const header = modal.querySelector('.sector-modal-header');
        header.textContent = sharesValue > 0 ? '修改持仓份额' : '设置持仓份额';

        modal.classList.add('active');
        setTimeout(() => sharesInput.focus(), 100);
    };

    // 关闭份额设置弹窗
    window.closeSharesModal = function() {
        const modal = document.getElementById('sharesModal');
        modal.classList.remove('active');
        currentSharesFundCode = null;
    };

    // 确认份额设置
    window.confirmShares = async function() {
        if (!currentSharesFundCode) {
            alert('基金代码无效');
            return;
        }

        const sharesInput = document.getElementById('sharesModalInput');
        const shares = parseFloat(sharesInput.value) || 0;

        if (shares < 0) {
            alert('份额不能为负数');
            return;
        }

        try {
            const response = await fetch('/api/fund/shares', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code: currentSharesFundCode, shares: shares })
            });
            const result = await response.json();
            if (result.success) {
                // 更新全局份额数据
                if (!window.fundSharesData) {
                    window.fundSharesData = {};
                }
                window.fundSharesData[currentSharesFundCode] = shares;

                // 更新按钮文本
                updateSharesButton(currentSharesFundCode, shares);
                // 重新计算持仓统计
                calculatePositionSummary();
                // 关闭弹窗
                closeSharesModal();
            } else {
                alert(result.message);
            }
        } catch (e) {
            alert('更新份额失败: ' + e.message);
        }
    };

    // 下载fund_map.json
    window.updateShares = async function(fundCode, shares) {
        if (!fundCode) {
            alert('基金代码无效');
            return;
        }

        try {
            const sharesValue = parseFloat(shares) || 0;
            const response = await fetch('/api/fund/shares', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code: fundCode, shares: sharesValue })
            });
            const result = await response.json();
            if (result.success) {
                // 更新全局份额数据
                if (!window.fundSharesData) {
                    window.fundSharesData = {};
                }
                window.fundSharesData[fundCode] = sharesValue;

                // 更新按钮状态
                updateSharesButton(fundCode, sharesValue);
                // 更新成功后重新计算持仓统计
                calculatePositionSummary();
            } else {
                alert(result.message);
            }
        } catch (e) {
            alert('更新份额失败: ' + e.message);
        }
    };

    // 下载fund_map.json
    window.downloadFundMap = function() {
        window.location.href = '/api/fund/download';
    };

    // 上传fund_map.json
    window.uploadFundMap = async function(file) {
        if (!file) {
            alert('请选择文件');
            return;
        }

        if (!file.name.endsWith('.json')) {
            alert('只支持JSON文件');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/fund/upload', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();
            if (result.success) {
                alert(result.message);
                location.reload();
            } else {
                alert(result.message);
            }
        } catch (e) {
            alert('上传失败: ' + e.message);
        }
    };

    // 计算并显示持仓统计
    async function calculatePositionSummary() {
        let totalValue = 0;
        let estimatedGain = 0;
        let actualGain = 0;
        let settledValue = 0;
        const today = new Date().toISOString().split('T')[0];

        // Get fund data map for holdings cards
        let fundDataMap = {};
        try {
            const response = await fetch('/api/fund/data');
            if (response.ok) {
                fundDataMap = await response.json();
            }
        } catch (e) {
            console.warn('Failed to fetch fund data map:', e);
        }

        // Collect held funds data for cards
        const heldFundsData = [];
        // Collect fund details for summary table
        const fundDetailsData = [];

        // 遍历所有基金行
        const fundRows = document.querySelectorAll('.style-table tbody tr');
        fundRows.forEach(row => {
            const cells = row.querySelectorAll('td');
            if (cells.length < 9) return;

            // 获取基金代码
            const codeCell = cells[1]; // 第二列是基金代码（第一列是复选框）
            const fundCode = codeCell.textContent.trim();

            // Check if this fund is held
            const isHeld = fundDataMap[fundCode]?.is_hold || false;

            // 获取份额数据（从全局数据对象）
            const shares = window.fundSharesData && window.fundSharesData[fundCode] ? parseFloat(window.fundSharesData[fundCode]) : 0;
            if (shares <= 0) return;  // 只处理有份额的基金

            try {
                // 解析净值 "1.234(2025-02-02)"
                const netValueText = cells[4].textContent.trim();
                const netValueMatch = netValueText.match(/([0-9.]+)\(([0-9-]+)\)/);
                if (!netValueMatch) return;

                const netValue = parseFloat(netValueMatch[1]);
                let netValueDate = netValueMatch[2];

                // 处理净值日期格式：API可能返回"MM-DD"或"YYYY-MM-DD"
                // 如果是"MM-DD"格式，添加当前年份
                if (netValueDate.length === 5) {  // 格式为"MM-DD"
                    const currentYear = new Date().getFullYear();
                    netValueDate = `${currentYear}-${netValueDate}`;
                }

                // 解析估值增长率
                const estimatedGrowthText = cells[5].textContent.trim();
                const estimatedGrowth = estimatedGrowthText !== 'N/A' ?
                    parseFloat(estimatedGrowthText.replace('%', '')) : 0;

                // 解析日涨幅
                const dayGrowthText = cells[6].textContent.trim();
                const dayGrowth = dayGrowthText !== 'N/A' ?
                    parseFloat(dayGrowthText.replace('%', '')) : 0;

                // 解析连涨/跌
                const consecutiveText = cells[7].textContent.trim();

                // 解析近30天
                const monthlyText = cells[8].textContent.trim();

                // 计算持仓市值
                const positionValue = shares * netValue;

                // If this fund is held, collect its data for cards
                if (isHeld) {
                    heldFundsData.push({
                        code: fundCode,
                        name: fundDataMap[fundCode]?.fund_name || 'Unknown',
                        sectors: fundDataMap[fundCode]?.sectors || [],
                        netValue: netValue,
                        netValueDate: netValueDate,
                        estimatedGrowth: estimatedGrowth,
                        dayGrowth: dayGrowth,
                        consecutive: consecutiveText,
                        monthly: monthlyText,
                        shares: shares,
                        positionValue: positionValue
                    });
                }

                if (shares > 0) {
                    totalValue += positionValue;

                    // 计算预估涨跌
                    const fundEstimatedGain = positionValue * estimatedGrowth / 100;
                    estimatedGain += fundEstimatedGain;

                    // 计算实际涨跌（仅当日结算）
                    let fundActualGain = 0;
                    if (netValueDate === today) {
                        fundActualGain = positionValue * dayGrowth / 100;
                        actualGain += fundActualGain;
                        settledValue += positionValue;
                    }

                    // Collect fund details for summary table
                    const fundName = cells[2].textContent.trim();
                    fundDetailsData.push({
                        code: fundCode,
                        name: fundName,
                        shares: shares,
                        positionValue: positionValue,
                        estimatedGain: fundEstimatedGain,
                        estimatedGainPct: estimatedGrowth,
                        actualGain: fundActualGain,
                        actualGainPct: netValueDate === today ? dayGrowth : 0
                    });
                }
            } catch (e) {
                console.warn('解析基金数据失败:', fundCode, e);
            }
        });

        // Update Asset Hero Section
        const assetHero = document.getElementById('assetHero');
        if (assetHero) {
            if (totalValue > 0) {
                assetHero.style.display = 'block';

            // Update total value
            document.getElementById('heroTotalValue').textContent =
                '¥' + totalValue.toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2});

            // Update estimated gain
            const estGainPct = totalValue > 0 ? (estimatedGain / totalValue * 100) : 0;
            const estSign = estimatedGain >= 0 ? '+' : '';
            const estClass = estimatedGain >= 0 ? 'positive' : 'negative';
            document.getElementById('heroEstimatedGain').textContent =
                estSign + '¥' + Math.abs(estimatedGain).toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            document.getElementById('heroEstimatedGain').className = 'asset-metric-value ' + estClass;
            document.getElementById('heroEstimatedGainPct').textContent = estSign + estGainPct.toFixed(2) + '%';

            // Update actual gain
            if (settledValue > 0) {
                const actGainPct = (actualGain / settledValue * 100);
                const actSign = actualGain >= 0 ? '+' : '';
                const actClass = actualGain >= 0 ? 'positive' : 'negative';
                document.getElementById('heroActualGain').textContent =
                    actSign + '¥' + Math.abs(actualGain).toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                document.getElementById('heroActualGain').className = 'asset-metric-value ' + actClass;
                document.getElementById('heroActualGainPct').textContent = actSign + actGainPct.toFixed(2) + '% (Settled)';
            } else {
                document.getElementById('heroActualGain').textContent = '¥0.00';
                document.getElementById('heroActualGain').className = 'asset-metric-value neutral';
                document.getElementById('heroActualGainPct').textContent = '0.00% (Settled)';
            }
            } else {
                assetHero.style.display = 'none';
            }
        }

        // Generate and populate holdings cards
        if (heldFundsData.length > 0) {
            const cardsHTML = heldFundsData.map(fund => {
                const sectorTags = fund.sectors && fund.sectors.length > 0
                    ? `<span style="color: #8b949e; font-size: 12px;"> 🏷️ ${fund.sectors.join(', ')}</span>`
                    : '';
                const estClass = fund.estimatedGrowth >= 0 ? 'up' : 'down';
                const dayClass = fund.dayGrowth >= 0 ? 'up' : 'down';

                return `
                <div class="fund-glass-card" data-code="${fund.code}">
                    <div class="card-header">
                        <div>
                            <div class="card-title">${fund.name}</div>
                            <div class="card-code">${fund.code} ${sectorTags}</div>
                        </div>
                        <div class="card-badge">⭐</div>
                    </div>
                    <div class="card-main-data">
                        <span class="est-pct ${estClass}">${fund.estimatedGrowth >= 0 ? '+' : ''}${fund.estimatedGrowth.toFixed(2)}%</span>
                        <span style="font-size: 12px; color: var(--text-dim)">实时估值</span>
                    </div>
                    <div class="card-details">
                        <div class="detail-item">持仓份额 <b>${fund.shares.toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</b></div>
                        <div class="detail-item">估值盈亏 <b class="${estClass}">${fund.estimatedGrowth >= 0 ? '+' : ''}¥${(fund.positionValue * fund.estimatedGrowth / 100).toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</b></div>
                        <div class="detail-item">当前净值 <b>${fund.netValue.toFixed(4)}</b></div>
                        <div class="detail-item">日涨幅 <b class="${dayClass}">${fund.dayGrowth >= 0 ? '+' : ''}${fund.dayGrowth.toFixed(2)}%</b></div>
                    </div>
                </div>
                `;
            }).join('');

            const holdingsSection = `
            <div style="margin-bottom: 24px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                    <div style="font-size: 18px; font-weight: 600; color: var(--text-main);">💎 核心持仓</div>
                    <div style="font-size: 14px; color: var(--text-dim); font-family: var(--font-mono);">${heldFundsData.length} 只</div>
                </div>
                <div class="holdings-grid">
                    ${cardsHTML}
                </div>
            </div>
            `;

            document.getElementById('holdingsCardsContainer').innerHTML = holdingsSection;
        } else {
            document.getElementById('holdingsCardsContainer').innerHTML = '';
        }

        // 显示或隐藏持仓统计区域
        const summaryDiv = document.getElementById('positionSummary');
        const fundDetailsDiv = document.getElementById('fundDetailsSummary');
        if (!summaryDiv) {
            // positionSummary element not found (sidebar layout), skip old layout summary
            console.log('positionSummary element not found - using sidebar layout');
        } else if (totalValue > 0) {
            summaryDiv.style.display = 'block';

            // 更新总持仓金额
            const totalValueEl = document.getElementById('totalValue');
            if (totalValueEl) {
                totalValueEl.textContent =
                    '¥' + totalValue.toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            }

            // 更新预估涨跌
            const estGainPct = totalValue > 0 ? (estimatedGain / totalValue * 100) : 0;
            const estSign = estimatedGain >= 0 ? '+' : '-';
            const estColor = estimatedGain >= 0 ? '#ef4444' : '#10b981';
            const estimatedGainEl = document.getElementById('estimatedGain');
            if (estimatedGainEl) {
                estimatedGainEl.innerHTML =
                    `<span class="sensitive-value ${estimatedGain >= 0 ? 'positive' : 'negative'}" style="color: ${estColor}"><span class="real-value">¥${Math.abs(estimatedGain).toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span><span class="hidden-value">****</span></span><span id="estimatedGainPct" style="color: ${estColor}"> (${estSign}${estGainPct.toFixed(2)}%)</span>`;
            }

            // 更新实际涨跌
            const actualGainEl = document.getElementById('actualGain');
            if (actualGainEl) {
                if (settledValue > 0) {
                    const actGainPct = (actualGain / settledValue * 100);
                    const actSign = actualGain >= 0 ? '+' : '-';
                    const actColor = actualGain >= 0 ? '#ef4444' : '#10b981';
                    actualGainEl.innerHTML =
                        `<span class="sensitive-value ${actualGain >= 0 ? 'positive' : 'negative'}" style="color: ${actColor}"><span class="real-value">¥${Math.abs(actualGain).toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span><span class="hidden-value">****</span></span><span id="actualGainPct" style="color: ${actColor}"> (${actSign}${actGainPct.toFixed(2)}%)</span>`;
                } else {
                    actualGainEl.innerHTML =
                        '<span style="color: var(--text-dim);">净值未更新</span>';
                }
            }

            // 填充分基金明细表格
            if (fundDetailsDiv && fundDetailsData.length > 0) {
                fundDetailsDiv.style.display = 'block';
                const tableBody = document.getElementById('fundDetailsTableBody');
                if (tableBody) {
                    tableBody.innerHTML = fundDetailsData.map(fund => {
                        const estColor = fund.estimatedGain >= 0 ? '#f44336' : '#4caf50';
                        const actColor = fund.actualGain >= 0 ? '#f44336' : '#4caf50';
                        const estSign = fund.estimatedGain >= 0 ? '+' : '';
                        const actSign = fund.actualGain >= 0 ? '+' : '';
                        return `
                            <tr style="border-bottom: 1px solid var(--border);">
                                <td style="padding: 10px; text-align: center; vertical-align: middle; color: var(--accent); font-weight: 500;">${fund.code}</td>
                                <td style="padding: 10px; text-align: center; vertical-align: middle; color: var(--text-main);">${fund.name}</td>
                                <td style="padding: 10px; text-align: center; vertical-align: middle; font-family: var(--font-mono);">${fund.shares.toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                                <td style="padding: 10px; text-align: center; vertical-align: middle; font-family: var(--font-mono); font-weight: 600;">¥${fund.positionValue.toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                                <td style="padding: 10px; text-align: center; vertical-align: middle; font-family: var(--font-mono); color: ${estColor}; font-weight: 500;">¥${Math.abs(fund.estimatedGain).toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                                <td style="padding: 10px; text-align: center; vertical-align: middle; font-family: var(--font-mono); color: ${estColor}; font-weight: 500;">${estSign}${fund.estimatedGainPct.toFixed(2)}%</td>
                                <td style="padding: 10px; text-align: center; vertical-align: middle; font-family: var(--font-mono); color: ${actColor}; font-weight: 500;">¥${Math.abs(fund.actualGain).toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                                <td style="padding: 10px; text-align: center; vertical-align: middle; font-family: var(--font-mono); color: ${actColor}; font-weight: 500;">${actSign}${fund.actualGainPct.toFixed(2)}%</td>
                            </tr>
                        `;
                    }).join('');
                }
            } else if (fundDetailsDiv) {
                fundDetailsDiv.style.display = 'none';
            }
        } else {
            summaryDiv.style.display = 'none';
            if (fundDetailsDiv) {
                fundDetailsDiv.style.display = 'none';
            }
        }
    }

    // 页面加载时加载份额数据并计算持仓统计
    async function loadSharesData() {
        try {
            // 从后端API获取用户的基金数据（包含份额）
            const response = await fetch('/api/fund/data');
            if (response.ok) {
                const fundData = await response.json();

                // 存储份额数据到全局变量
                window.fundSharesData = {};

                // 先存储数据，稍后更新按钮
                for (const [code, data] of Object.entries(fundData)) {
                    const shares = parseFloat(data.shares) || 0;
                    window.fundSharesData[code] = shares;
                }

                // 等待DOM加载完成后更新按钮状态
                updateAllSharesButtons();

                // 计算持仓统计
                calculatePositionSummary();
            }
        } catch (e) {
            console.error('加载份额数据失败:', e);
            // 即使加载失败，也尝试计算持仓统计
            calculatePositionSummary();
        }
    }

    // 更新所有份额按钮状态（在DOM加载后调用）
    function updateAllSharesButtons() {
        if (!window.fundSharesData) return;

        for (const [code, shares] of Object.entries(window.fundSharesData)) {
            updateSharesButton(code, shares);
        }
    }

    // 板块搜索功能
    document.addEventListener('DOMContentLoaded', function() {
        const searchInput = document.getElementById('sectorSearch');
        if (searchInput) {
            searchInput.addEventListener('input', function() {
                const keyword = this.value.toLowerCase();
                const categories = document.querySelectorAll('.sector-category');

                categories.forEach(category => {
                    const items = category.querySelectorAll('.sector-item');
                    let hasVisible = false;

                    items.forEach(item => {
                        const text = item.textContent.toLowerCase();
                        if (text.includes(keyword)) {
                            item.style.display = 'block';
                            hasVisible = true;
                        } else {
                            item.style.display = 'none';
                        }
                    });

                    category.style.display = hasVisible || keyword === '' ? 'block' : 'none';
                });
            });
        }

        // 初始化 - 加载份额数据
        loadSharesData();

        // 份额弹窗 - 点击外部关闭
        const sharesModal = document.getElementById('sharesModal');
        if (sharesModal) {
            sharesModal.addEventListener('click', function(e) {
                if (e.target === sharesModal) {
                    closeSharesModal();
                }
            });

            // 份额弹窗 - 回车键确认
            const sharesInput = document.getElementById('sharesModalInput');
            if (sharesInput) {
                sharesInput.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        confirmShares();
                    }
                });
            }
        }
    });
    </script>
    """


# ==================== 新页面布局函数 ====================


def get_market_page_html(market_data, username=None):
    """生成市场行情页面 - 使用卡片/图表布局"""
    css_style = get_css_style()

    # 生成市场数据卡片
    market_cards = ""
    for key, data in market_data.items():
        card_id = "card-{}".format(key)
        icon = get_market_icon(key)
        market_cards += """
        <div class="market-card" id="{card_id}">
            <div class="market-card-header">
                <h3 class="market-card-title">
                    <span class="card-icon">{icon}</span>
                    {title}
                </h3>
                <button class="card-toggle" onclick="toggleCard('{card_id}')">
                    <span>▼</span>
                </button>
            </div>
            <div class="market-card-content">
                {content}
            </div>
        </div>
        """.format(
            card_id=card_id, icon=icon, title=data["title"], content=data["content"]
        )

    username_display = ""
    if username:
        username_display = '<span class="nav-user"><i class="ri-user-smile-line"></i> {username}</span>'.format(
            username=username
        )
        username_display += '<a href="/logout" class="nav-logout">退出登录</a>'

    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>市场行情 - LanFund</title>
    <link rel="icon" href="/static/1.ico">
    {css_style}
    <link rel="stylesheet" href="/static/css/style.css">
    <style>
        body {{
            background-color: var(--terminal-bg);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}

        /* 顶部导航栏 */
        .top-navbar {{
            background-color: var(--card-bg);
            color: var(--text-main);
            padding: 0.8rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
        }}

        .top-navbar-brand {{
            display: flex;
            align-items: center;
            flex: 0 0 auto;
        }}

        .top-navbar-quote {{
            flex: 1;
            text-align: center;
            font-size: 1rem;
            font-weight: 500;
            color: var(--text-main);
            font-style: italic;
            padding: 0 2rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            letter-spacing: 0.05em;
            transition: opacity 0.5s ease-in-out;
        }}

        .top-navbar-menu {{
            display: flex;
            gap: 1rem;
            align-items: center;
        }}

        .nav-user {{
            color: #3b82f6;
            font-weight: 500;
        }}

        .nav-logout {{
            color: #f85149;
            text-decoration: none;
            font-weight: 500;
        }}

        /* 主容器 */
        .main-container {{
            display: flex;
            flex: 1;
        }}

        /* 内容区域 */
        .content-area {{
            flex: 1;
            padding: 30px;
            overflow-y: auto;
        }}

        .page-header {{
            margin-bottom: 30px;
            text-align: center;
        }}

        .page-header h1 {{
            font-size: 2rem;
            font-weight: 700;
            margin: 0;
            border: none;
            text-decoration: none;
            background: linear-gradient(135deg, var(--accent), var(--down));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .page-header p {{
            color: var(--text-dim);
            margin-top: 10px;
            border: none;
            text-decoration: none;
        }}

        /* 市场行情网格布局 */
        .market-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            max-width: 1600px;
            margin: 0 auto;
        }}

        @media (max-width: 1200px) {{
            .market-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        /* 市场卡片 */
        .market-card {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
            transition: all 0.3s ease;
        }}

        .market-card:hover {{
            border-color: var(--accent);
            box-shadow: 0 4px 20px rgba(59, 130, 246, 0.15);
        }}

        .market-card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 20px;
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
            border-bottom: 1px solid var(--border);
            cursor: pointer;
            user-select: none;
        }}

        .market-card-title {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin: 0;
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--text-main);
        }}

        .card-icon {{
            font-size: 1.3rem;
        }}

        .card-toggle {{
            background: none;
            border: none;
            color: var(--text-dim);
            cursor: pointer;
            padding: 4px 8px;
            transition: transform 0.3s ease;
        }}

        .card-toggle.collapsed {{
            transform: rotate(-90deg);
        }}

        .market-card-content {{
            padding: 20px;
            max-height: 600px;
            overflow-y: auto;
            transition: all 0.3s ease;
            opacity: 1;
        }}

        /* 折叠状态：内容隐藏 */
        .market-card.collapsed .market-card-content {{
            display: none;
        }}

        /* 折叠状态：卡片收缩 */
        .market-card.collapsed {{
            max-height: 60px;
        }}

        /* 滚动条样式 */
        .market-card-content::-webkit-scrollbar {{
            width: 8px;
        }}

        .market-card-content::-webkit-scrollbar-track {{
            background: var(--terminal-bg);
        }}

        .market-card-content::-webkit-scrollbar-thumb {{
            background: var(--border);
            border-radius: 4px;
        }}

        .market-card-content::-webkit-scrollbar-thumb:hover {{
            background: var(--accent);
        }}

        @media (max-width: 768px) {{
            .main-container {{
                flex-direction: column;
            }}

            .sidebar {{
                width: 100%;
                border-right: none;
                border-bottom: 1px solid var(--border);
                padding: 10px 0;
            }}

            .sidebar-item {{
                padding: 10px 15px;
                font-size: 0.9rem;
            }}

            .content-area {{
                padding: 15px;
            }}

            .top-navbar {{
                padding: 0.6rem 1rem;
            }}

            .top-navbar-quote {{
                font-size: 0.75rem;
                padding: 0 0.5rem;
            }}
        }}
    </style>
</head>
<body>
    <!-- 顶部导航栏 -->
    <nav class="top-navbar">
        <div class="top-navbar-brand">
            <img src="/static/1.ico" alt="Logo" class="navbar-logo">
        </div>
        <div class="top-navbar-quote" id="lyricsDisplay">
            偶然与巧合, 舞动了蝶翼, 谁的心头风起 ————《如果我们不曾相遇》
        </div>
        <div class="top-navbar-menu">
            {username_display}
        </div>
    </nav>

    <!-- 主容器 -->
    <div class="main-container">
        <!-- 左侧导航栏 -->
        <div class="sidebar">
            <a href="/market" class="sidebar-item active">
                <span>📊</span>
                <span>市场行情</span>
            </a>
            <a href="/portfolio" class="sidebar-item">
                <span>💼</span>
                <span>持仓基金</span>
            </a>
            <a href="/sectors" class="sidebar-item">
                <span>🏢</span>
                <span>行业板块</span>
            </a>
        </div>

        <!-- 内容区域 -->
        <div class="content-area">
            <!-- 页面标题 -->
            <div class="page-header">
                <h1>📊 市场行情</h1>
                <p>实时追踪全球市场动态</p>
            </div>

            <!-- 市场数据网格 -->
            <div class="market-grid">
                {market_cards}
            </div>
        </div>
    </div>

    <script>
        function toggleCard(cardId) {{
            const card = document.getElementById(cardId);
            const toggle = card.querySelector('.card-toggle');
            card.classList.toggle('collapsed');
            toggle.classList.toggle('collapsed');
        }}

        // 自动颜色化
        function autoColorize() {{
            const cells = document.querySelectorAll('.style-table td');
            cells.forEach(cell => {{
                const text = cell.textContent.trim();
                const cleanText = text.replace(/[%,亿万手]/g, '');
                const val = parseFloat(cleanText);

                if (!isNaN(val)) {{
                    if (text.includes('%') || text.includes('涨跌')) {{
                        if (text.includes('-')) {{
                            cell.classList.add('negative');
                        }} else if (val > 0) {{
                            cell.classList.add('positive');
                        }}
                    }} else if (text.startsWith('-')) {{
                        cell.classList.add('negative');
                    }} else if (text.startsWith('+')) {{
                        cell.classList.add('positive');
                    }}
                }}
            }});
        }}

        document.addEventListener('DOMContentLoaded', function() {{
            autoColorize();
        }});
    </script>
</body>
</html>""".format(
        css_style=css_style,
        username_display=username_display,
        market_cards=market_cards,
    )
    return html


def get_news_page_html(news_content, username=None):
    """生成7*24快讯页面 - 简洁布局"""
    css_style = get_css_style()

    username_display = ""
    if username:
        username_display = '<span class="nav-user"><i class="ri-user-smile-line"></i> {username}</span>'.format(
            username=username
        )
        username_display += '<a href="/logout" class="nav-logout">退出登录</a>'

    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>7*24快讯 - LanFund</title>
    <link rel="icon" href="/static/1.ico">
    {css_style}
    <link rel="stylesheet" href="/static/css/style.css">
    <style>
        body {{
            background-color: var(--terminal-bg);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}

        /* 顶部导航栏 */
        .top-navbar {{
            background-color: var(--card-bg);
            color: var(--text-main);
            padding: 0.8rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
        }}

        .top-navbar-brand {{
            display: flex;
            align-items: center;
            flex: 0 0 auto;
        }}

        .navbar-logo {{
            width: 32px;
            height: 32px;
        }}

        .top-navbar-quote {{
            flex: 1;
            text-align: center;
            font-size: 1rem;
            font-weight: 500;
            color: var(--text-main);
            font-style: italic;
            padding: 0 2rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            letter-spacing: 0.05em;
            transition: opacity 0.5s ease-in-out;
        }}

        .top-navbar-menu {{
            display: flex;
            gap: 1rem;
            align-items: center;
        }}

        .nav-logout {{
            color: #f85149;
            text-decoration: none;
            font-weight: 500;
        }}

        .nav-user {{
            color: #3b82f6;
            font-weight: 500;
        }}

        /* 主容器 */
        .main-container {{
            display: flex;
            flex: 1;
        }}

        /* 内容区域 */
        .content-area {{
            flex: 1;
            padding: 20px;
            overflow-y: auto;
        }}

        /* 隐藏滚动条但保留功能 */
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}

        ::-webkit-scrollbar-track {{
            background: transparent;
        }}

        ::-webkit-scrollbar-thumb {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: rgba(255, 255, 255, 0.2);
        }}

        /* Firefox */
        * {{
            scrollbar-width: thin;
            scrollbar-color: rgba(255, 255, 255, 0.1) transparent;
        }}

        .page-header {{
            margin-bottom: 20px;
        }}

        .page-header h1 {{
            font-size: 1.8rem;
            margin: 0;
            color: var(--text-main);
        }}

        .page-header p {{
            margin: 5px 0 0;
            color: var(--text-dim);
        }}

        /* 快讯内容 */
        .news-content {{
            background-color: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 20px;
            max-height: calc(100vh - 200px);
            overflow-y: auto;
        }}

        /* 响应式设计 */
        @media (max-width: 768px) {{
            .sidebar {{
                display: none;
            }}

            .content-area {{
                padding: 15px;
            }}

            .top-navbar {{
                padding: 0.6rem 1rem;
            }}

            .top-navbar-quote {{
                font-size: 0.75rem;
                padding: 0 0.5rem;
            }}
        }}
    </style>
</head>
<body>
    <!-- 顶部导航栏 -->
    <nav class="top-navbar">
        <div class="top-navbar-brand">
            <img src="/static/1.ico" alt="Logo" class="navbar-logo">
        </div>
        <div class="top-navbar-quote" id="lyricsDisplay">
            偶然与巧合, 舞动了蝶翼, 谁的心头风起 ————《如果我们不曾相遇》
        </div>
        <div class="top-navbar-menu">
            {username_display}
        </div>
    </nav>

    <!-- 主容器 -->
    <div class="main-container">
        <!-- 左侧导航栏 -->
        <div class="sidebar collapsed" id="sidebar">
            <div class="sidebar-toggle" id="sidebarToggle"><i class="ri-arrow-right-s-line"></i></div>
            <a href="/market" class="sidebar-item active">
                <span class="sidebar-icon"><i class="ri-newspaper-line"></i></span>
                <span>7*24快讯</span>
            </a>
            <a href="/market-indices" class="sidebar-item">
                <span class="sidebar-icon"><i class="ri-bar-chart-2-line"></i></span>
                <span>市场指数</span>
            </a>
            <a href="/precious-metals" class="sidebar-item">
                <span class="sidebar-icon">🪙</span>
                <span>贵金属行情</span>
            </a>
            <a href="/portfolio" class="sidebar-item">
                <span class="sidebar-icon"><i class="ri-briefcase-4-line"></i></span>
                <span>持仓基金</span>
            </a>
            <a href="/sectors" class="sidebar-item">
                <span class="sidebar-icon"><i class="ri-building-4-line"></i></span>
                <span>行业板块</span>
            </a>
        </div>

        <!-- 内容区域 -->
        <div class="content-area">
            <!-- 页面标题 -->
            <div class="page-header">
                <h1 style="display: flex; align-items: center;">
                    <i class="ri-newspaper-line"></i> 7*24快讯
                    <button id="refreshBtn" onclick="refreshCurrentPage()" class="refresh-button" style="margin-left: 15px; padding: 8px 16px; background: var(--accent); color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-weight: 500; transition: all 0.2s ease; display: inline-flex; align-items: center; gap: 5px;">🔄 刷新</button>
                </h1>
                <p>实时追踪全球市场动态</p>
            </div>

            <!-- 快讯内容 -->
            <div class="news-content">
                {news_content}
            </div>
        </div>
    </div>

    <script src="/static/js/main.js"></script>
    <script src="/static/js/sidebar-nav.js"></script>
    <script>
        // 自动颜色化
        function autoColorize() {{
            const elements = document.querySelectorAll('[data-change]');
            elements.forEach(function(el) {{
                const change = parseFloat(el.getAttribute('data-change'));
                if (change > 0) {{
                    el.style.color = '#f44336';
                }} else if (change < 0) {{
                    el.style.color = '#4caf50';
                }}
            }});
        }}

        document.addEventListener('DOMContentLoaded', function() {{
            // 歌词轮播
            const lyrics = [
                '总要有一首我的歌, 大声唱过, 再看天地辽阔 ————《一颗苹果》',
                '苍狗又白云, 身旁有了你, 匆匆轮回又有何惧 ————《如果我们不曾相遇》',
                '活着其实很好, 再吃一颗苹果 ————《一颗苹果》',
                '偶然与巧合, 舞动了蝶翼, 谁的心头风起 ————《如果我们不曾相遇》'
            ];
            let currentLyricIndex = 0;
            const lyricsElement = document.getElementById('lyricsDisplay');

            // 随机选择初始歌词
            currentLyricIndex = Math.floor(Math.random() * lyrics.length);
            if (lyricsElement) {{
                lyricsElement.textContent = lyrics[currentLyricIndex];

                // 每10秒切换一次歌词
                setInterval(function() {{
                    // 淡出
                    lyricsElement.style.opacity = '0';

                    setTimeout(function() {{
                        // 切换歌词
                        currentLyricIndex = (currentLyricIndex + 1) % lyrics.length;
                        lyricsElement.textContent = lyrics[currentLyricIndex];

                        // 淡入
                        lyricsElement.style.opacity = '1';
                    }}, 500);
                }}, 10000);
            }}

            autoColorize();
        }});
    </script>
</body>
</html>""".format(
        css_style=css_style,
        username_display=username_display,
        news_content=news_content,
    )
    return html


def get_precious_metals_page_html(metals_data, username=None):
    """生成贵金属行情页面"""
    css_style = get_css_style()

    username_display = ""
    if username:
        username_display = '<span class="nav-user"><i class="ri-user-smile-line"></i> {username}</span>'.format(
            username=username
        )
        username_display += '<a href="/logout" class="nav-logout">退出登录</a>'

    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>贵金属行情 - LanFund</title>
    <link rel="icon" href="/static/1.ico">
    {css_style}
    <link rel="stylesheet" href="/static/css/style.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        body {{
            background-color: var(--terminal-bg);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}

        /* 顶部导航栏 */
        .top-navbar {{
            background-color: var(--card-bg);
            color: var(--text-main);
            padding: 0.8rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
        }}

        .top-navbar-brand {{
            display: flex;
            align-items: center;
            flex: 0 0 auto;
        }}

        .navbar-logo {{
            width: 32px;
            height: 32px;
        }}

        .top-navbar-quote {{
            flex: 1;
            text-align: center;
            font-size: 1rem;
            font-weight: 500;
            color: var(--text-main);
            font-style: italic;
            padding: 0 2rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            letter-spacing: 0.05em;
            transition: opacity 0.5s ease-in-out;
        }}

        .top-navbar-menu {{
            display: flex;
            gap: 1rem;
            align-items: center;
        }}

        .nav-logout {{
            color: #f85149;
            text-decoration: none;
            font-weight: 500;
        }}

        .nav-user {{
            color: #3b82f6;
            font-weight: 500;
        }}

        /* 主容器 */
        .main-container {{
            display: flex;
            flex: 1;
        }}

        /* 内容区域 */
        .content-area {{
            flex: 1;
            padding: 20px;
            overflow-y: auto;
        }}

        /* 隐藏滚动条但保留功能 */
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}

        ::-webkit-scrollbar-track {{
            background: transparent;
        }}

        ::-webkit-scrollbar-thumb {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: rgba(255, 255, 255, 0.2);
        }}

        /* Firefox */
        * {{
            scrollbar-width: thin;
            scrollbar-color: rgba(255, 255, 255, 0.1) transparent;
        }}

        .page-header {{
            margin-bottom: 20px;
        }}

        .page-header h1 {{
            font-size: 1.8rem;
            margin: 0;
            color: var(--text-main);
        }}

        .page-header p {{
            margin: 5px 0 0;
            color: var(--text-dim);
        }}

        /* 贵金属网格布局 - 上下两栏 */
        .metals-grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 20px;
            max-width: 100%;
        }}

        .metal-card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
            width: 100%;
        }}

        .metal-card-realtime {{
            min-height: 200px;
        }}

        .metal-card-history {{
            min-height: 400px;
        }}

        .metal-card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
        }}

        .metal-card-header {{
            padding: 15px 20px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .metal-card-title {{
            font-size: 1.1rem;
            font-weight: 500;
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .metal-card-content {{
            padding: 20px;
            max-height: 500px;
            overflow-y: auto;
        }}

        .chart-container {{
            position: relative;
            height: 400px;
            width: 100%;
        }}

        /* 响应式设计 */
        @media (max-width: 768px) {{
            .sidebar {{
                display: none;
            }}

            .metals-grid {{
                grid-template-columns: 1fr;
            }}

            .content-area {{
                padding: 15px;
            }}

            .top-navbar {{
                padding: 0.6rem 1rem;
            }}

            .top-navbar-quote {{
                font-size: 0.75rem;
                padding: 0 0.5rem;
            }}

            .metal-card-history {{
                min-height: 300px;
            }}

            .chart-container {{
                height: 280px;
            }}
        }}
    </style>
</head>
<body>
    <!-- 顶部导航栏 -->
    <nav class="top-navbar">
        <div class="top-navbar-brand">
            <img src="/static/1.ico" alt="Logo" class="navbar-logo">
        </div>
        <div class="top-navbar-quote" id="lyricsDisplay">
            偶然与巧合, 舞动了蝶翼, 谁的心头风起 ————《如果我们不曾相遇》
        </div>
        <div class="top-navbar-menu">
            {username_display}
        </div>
    </nav>

    <!-- 主容器 -->
    <div class="main-container">
        <!-- 左侧导航栏 -->
        <div class="sidebar collapsed" id="sidebar">
            <div class="sidebar-toggle" id="sidebarToggle"><i class="ri-arrow-right-s-line"></i></div>
            <a href="/market" class="sidebar-item">
                <span class="sidebar-icon"><i class="ri-newspaper-line"></i></span>
                <span>7*24快讯</span>
            </a>
            <a href="/market-indices" class="sidebar-item">
                <span class="sidebar-icon"><i class="ri-bar-chart-2-line"></i></span>
                <span>市场指数</span>
            </a>
            <a href="/precious-metals" class="sidebar-item active">
                <span class="sidebar-icon">🪙</span>
                <span>贵金属行情</span>
            </a>
            <a href="/portfolio" class="sidebar-item">
                <span class="sidebar-icon"><i class="ri-briefcase-4-line"></i></span>
                <span>持仓基金</span>
            </a>
            <a href="/sectors" class="sidebar-item">
                <span class="sidebar-icon"><i class="ri-building-4-line"></i></span>
                <span>行业板块</span>
            </a>
        </div>

        <!-- 内容区域 -->
        <div class="content-area">
            <!-- 页面标题 -->
            <div class="page-header">
                <h1 style="display: flex; align-items: center;">
                    🪙 贵金属行情
                    <button id="refreshBtn" onclick="refreshCurrentPage()" class="refresh-button" style="margin-left: 15px; padding: 8px 16px; background: var(--accent); color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-weight: 500; transition: all 0.2s ease; display: inline-flex; align-items: center; gap: 5px;">🔄 刷新</button>
                </h1>
                <p>实时追踪贵金属价格走势</p>
            </div>

            <!-- 贵金属网格 - 上下两栏布局 -->
            <div class="metals-grid">
                <!-- 实时贵金属 -->
                <div class="metal-card metal-card-realtime">
                    <div class="metal-card-header">
                        <h3 class="metal-card-title">
                            <span>⚡</span>
                            <span>实时贵金属</span>
                        </h3>
                    </div>
                    <div class="metal-card-content">
                        {real_time_content}
                    </div>
                </div>

                <!-- 历史金价 -->
                <div class="metal-card metal-card-history">
                    <div class="metal-card-header">
                        <h3 class="metal-card-title">
                            <span>📈</span>
                            <span>历史金价</span>
                        </h3>
                    </div>
                    <div class="metal-card-content">
                        <!-- Hidden div to store history data for parsing -->
                        <div id="goldHistoryData" style="display:none;">
                            {history_content}
                        </div>
                        <div class="chart-container">
                            <canvas id="goldPriceChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="/static/js/main.js"></script>
    <script src="/static/js/sidebar-nav.js"></script>
    <script>
        // 自动颜色化
        function autoColorize() {{
            const elements = document.querySelectorAll('[data-change]');
            elements.forEach(function(el) {{
                const change = parseFloat(el.getAttribute('data-change'));
                if (change > 0) {{
                    el.style.color = '#f44336';
                }} else if (change < 0) {{
                    el.style.color = '#4caf50';
                }}
            }});
        }}

        // 解析历史金价数据并创建图表
        function createGoldChart() {{
            // 从隐藏的div中获取历史金价表格
            const historyContainer = document.getElementById('goldHistoryData');
            if (!historyContainer) return;

            const table = historyContainer.querySelector('table');
            if (!table) return;

            const rows = table.querySelectorAll('tbody tr');
            const labels = [];
            const prices = [];

            rows.forEach(row => {{
                const cells = row.querySelectorAll('td');
                if (cells.length >= 2) {{
                    labels.push(cells[0].textContent.trim());
                    prices.push(parseFloat(cells[1].textContent.trim()));
                }}
            }});

            // 创建图表
            const ctx = document.getElementById('goldPriceChart').getContext('2d');

            // 注册插件以在数据点上显示数值
            const dataLabelPlugin = {{
                id: 'dataLabelPlugin',
                afterDatasetsDraw(chart, args, options) {{
                    const {{ ctx }} = chart;
                    chart.data.datasets.forEach((dataset, datasetIndex) => {{
                        const meta = chart.getDatasetMeta(datasetIndex);
                        meta.data.forEach((datapoint, index) => {{
                            const value = dataset.data[index];
                            const x = datapoint.x;
                            const y = datapoint.y;

                            ctx.save();
                            ctx.fillStyle = '#f59e0b';
                            ctx.font = 'bold 11px sans-serif';
                            ctx.textAlign = 'center';
                            ctx.textBaseline = 'bottom';
                            ctx.fillText(value.toFixed(2), x, y - 5);
                            ctx.restore();
                        }});
                    }});
                }}
            }};

            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: labels.reverse(),
                    datasets: [{{
                        label: '金价 (元/克)',
                        data: prices.reverse(),
                        borderColor: '#f59e0b',
                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: 4,
                        pointBackgroundColor: '#f59e0b',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointHoverRadius: 6
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            labels: {{
                                color: '#9ca3af'
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            ticks: {{
                                color: '#9ca3af'
                            }},
                            grid: {{
                                color: 'rgba(255, 255, 255, 0.1)'
                            }}
                        }},
                        y: {{
                            ticks: {{
                                color: '#9ca3af'
                            }},
                            grid: {{
                                color: 'rgba(255, 255, 255, 0.1)'
                            }}
                        }}
                    }}
                }},
                plugins: [dataLabelPlugin]
            }});
        }}

        document.addEventListener('DOMContentLoaded', function() {{
            // 歌词轮播
            const lyrics = [
                '总要有一首我的歌, 大声唱过, 再看天地辽阔 ————《一颗苹果》',
                '苍狗又白云, 身旁有了你, 匆匆轮回又有何惧 ————《如果我们不曾相遇》',
                '活着其实很好, 再吃一颗苹果 ————《一颗苹果》',
                '偶然与巧合, 舞动了蝶翼, 谁的心头风起 ————《如果我们不曾相遇》'
            ];
            let currentLyricIndex = 0;
            const lyricsElement = document.getElementById('lyricsDisplay');

            // 随机选择初始歌词
            currentLyricIndex = Math.floor(Math.random() * lyrics.length);
            if (lyricsElement) {{
                lyricsElement.textContent = lyrics[currentLyricIndex];

                // 每10秒切换一次歌词
                setInterval(function() {{
                    // 淡出
                    lyricsElement.style.opacity = '0';

                    setTimeout(function() {{
                        // 切换歌词
                        currentLyricIndex = (currentLyricIndex + 1) % lyrics.length;
                        lyricsElement.textContent = lyrics[currentLyricIndex];

                        // 淡入
                        lyricsElement.style.opacity = '1';
                    }}, 500);
                }}, 10000);
            }}

            autoColorize();
            createGoldChart();
        }});
    </script>
</body>
</html>""".format(
        css_style=css_style,
        username_display=username_display,
        real_time_content=metals_data.get("real_time", ""),
        history_content=metals_data.get("history", ""),
    )
    return html


def get_market_indices_page_html(market_charts=None, chart_data=None, username=None):
    """生成市场指数页面 - 全球指数和成交量趋势"""
    css_style = get_css_style()
    import json

    username_display = ""
    if username:
        username_display = '<span class="nav-user"><i class="ri-user-smile-line"></i> {username}</span>'.format(
            username=username
        )
        username_display += '<a href="/logout" class="nav-logout">退出登录</a>'

    # 准备图表数据JSON (optional, for future chart enhancements)
    indices_data_json = json.dumps(
        chart_data.get("indices", {"labels": [], "prices": [], "changes": []})
        if chart_data
        else {"labels": [], "prices": [], "changes": []}
    )
    volume_data_json = json.dumps(
        chart_data.get(
            "volume", {"labels": [], "total": [], "sh": [], "sz": [], "bj": []}
        )
        if chart_data
        else {"labels": [], "total": [], "sh": [], "sz": [], "bj": []}
    )

    # 生成市场指数HTML - 两行布局
    market_content = """
        <!-- 市场指数区域 -->
        <div class="market-indices-section" style="padding: 30px;">
            <div class="page-header" style="margin-bottom: 25px;">
                <h1 style="font-size: 1.5rem; font-weight: 600; margin: 0; color: var(--text-main); display: flex; align-items: center;">
                    <i class="ri-bar-chart-2-line"></i> 市场指数
                    <button id="refreshBtn" onclick="refreshCurrentPage()" class="refresh-button" style="margin-left: 15px; padding: 8px 16px; background: var(--accent); color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-weight: 500; transition: all 0.2s ease; display: inline-flex; align-items: center; gap: 5px;">🔄 刷新</button>
                </h1>
            </div>

            <!-- 第一行：全球指数和成交量趋势 -->
            <div class="market-charts-grid" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 20px;">
                <!-- 全球指数 - 表格 -->
                <div class="chart-card" style="background-color: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; overflow: hidden;">
                    <div class="chart-card-header" style="padding: 12px 15px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="margin: 0; font-size: 1rem; color: var(--text-main);">🌍 全球指数</h3>
                    </div>
                    <div class="chart-card-content" style="padding: 15px; max-height: 400px; overflow-y: auto;">
                        {indices_content}
                    </div>
                </div>
                <!-- 成交量趋势 - 表格 -->
                <div class="chart-card" style="background-color: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; overflow: hidden;">
                    <div class="chart-card-header" style="padding: 12px 15px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="margin: 0; font-size: 1rem; color: var(--text-main);"><i class="ri-bar-chart-grouped-line"></i> 成交量趋势</h3>
                    </div>
                    <div class="chart-card-content" style="padding: 15px; max-height: 400px; overflow-y: auto;">
                        {volume_content}
                    </div>
                </div>
            </div>
        </div>
    """.format(
        indices_content=market_charts.get("indices", ""),
        volume_content=market_charts.get("volume", ""),
    )

    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>市场指数 - LanFund</title>
    <link rel="icon" href="/static/1.ico">
    {css_style}
    <link rel="stylesheet" href="/static/css/style.css">
    <style>
        body {{
            background-color: var(--terminal-bg);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}

        /* 顶部导航栏 */
        .top-navbar {{
            background-color: var(--card-bg);
            color: var(--text-main);
            padding: 0.8rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
        }}

        .top-navbar-brand {{
            display: flex;
            align-items: center;
            flex: 0 0 auto;
        }}

        .top-navbar-quote {{
            flex: 1;
            text-align: center;
            font-size: 1rem;
            font-weight: 500;
            color: var(--text-main);
            font-style: italic;
            padding: 0 2rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            letter-spacing: 0.05em;
            transition: opacity 0.5s ease-in-out;
        }}

        .top-navbar-menu {{
            display: flex;
            gap: 1rem;
            align-items: center;
        }}

        .nav-user {{
            color: #3b82f6;
            font-weight: 500;
        }}

        .nav-logout {{
            color: #f85149;
            text-decoration: none;
            font-weight: 500;
        }}

        /* 主容器 */
        .main-container {{
            display: flex;
            flex: 1;
        }}

        /* 内容区域 */
        .content-area {{
            flex: 1;
            overflow-y: auto;
        }}

        /* 隐藏滚动条但保留功能 */
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}

        ::-webkit-scrollbar-track {{
            background: transparent;
        }}

        ::-webkit-scrollbar-thumb {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: rgba(255, 255, 255, 0.2);
        }}

        /* Firefox */
        * {{
            scrollbar-width: thin;
            scrollbar-color: rgba(255, 255, 255, 0.1) transparent;
        }}

        .chart-card-content::-webkit-scrollbar {{
            width: 4px;
        }}

        .chart-card-content::-webkit-scrollbar-thumb {{
            background: rgba(255, 255, 255, 0.05);
        }}
    </style>
</head>
<body>
    <!-- 顶部导航栏 -->
    <div class="top-navbar">
        <div class="top-navbar-brand">
            <img src="/static/1.ico" alt="Logo" class="navbar-logo">
        </div>
        <div class="top-navbar-quote" id="lyricsDisplay">
            偶然与巧合, 舞动了蝶翼, 谁的心头风起 ————《如果我们不曾相遇》
        </div>
        <div class="top-navbar-menu">
            {username_display}
        </div>
    </div>

    <!-- 主容器 -->
    <div class="main-container">
        <!-- 左侧导航栏 -->
        <div class="sidebar collapsed" id="sidebar">
            <div class="sidebar-toggle" id="sidebarToggle"><i class="ri-arrow-right-s-line"></i></div>
            <a href="/market" class="sidebar-item">
                <span class="sidebar-icon"><i class="ri-newspaper-line"></i></span>
                <span>市场行情</span>
            </a>
            <a href="/market-indices" class="sidebar-item active">
                <span class="sidebar-icon"><i class="ri-bar-chart-2-line"></i></span>
                <span>市场指数</span>
            </a>
            <a href="/precious-metals" class="sidebar-item">
                <span class="sidebar-icon">🪙</span>
                <span>贵金属行情</span>
            </a>
            <a href="/portfolio" class="sidebar-item">
                <span class="sidebar-icon"><i class="ri-briefcase-4-line"></i></span>
                <span>持仓基金</span>
            </a>
            <a href="/sectors" class="sidebar-item">
                <span class="sidebar-icon"><i class="ri-building-4-line"></i></span>
                <span>行业板块</span>
            </a>
        </div>

        <!-- 内容区域 -->
        <div class="content-area">
            {market_content}
        </div>
    </div>

    <script src="/static/js/main.js"></script>
    <script src="/static/js/sidebar-nav.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            // 歌词轮播
            const lyrics = [
                '总要有一首我的歌, 大声唱过, 再看天地辽阔 ————《一颗苹果》',
                '苍狗又白云, 身旁有了你, 匆匆轮回又有何惧 ————《如果我们不曾相遇》',
                '活着其实很好, 再吃一颗苹果 ————《一颗苹果》',
                '偶然与巧合, 舞动了蝶翼, 谁的心头风起 ————《如果我们不曾相遇》'
            ];
            let currentLyricIndex = 0;
            const lyricsElement = document.getElementById('lyricsDisplay');

            // 随机选择初始歌词
            currentLyricIndex = Math.floor(Math.random() * lyrics.length);
            if (lyricsElement) {{
                lyricsElement.textContent = lyrics[currentLyricIndex];

                // 每10秒切换一次歌词
                setInterval(function() {{
                    // 淡出
                    lyricsElement.style.opacity = '0';

                    setTimeout(function() {{
                        // 切换歌词
                        currentLyricIndex = (currentLyricIndex + 1) % lyrics.length;
                        lyricsElement.textContent = lyrics[currentLyricIndex];

                        // 淡入
                        lyricsElement.style.opacity = '1';
                    }}, 500);
                }}, 10000);
            }}

            // 自动颜色化
            const cells = document.querySelectorAll('.style-table td');
            cells.forEach(cell => {{
                const text = cell.textContent.trim();
                const cleanText = text.replace(/[%,亿万手]/g, '');
                const val = parseFloat(cleanText);

                if (!isNaN(val)) {{
                    if (text.includes('%') || text.includes('涨跌')) {{
                        if (text.includes('-')) {{
                            cell.classList.add('negative');
                        }} else if (val > 0) {{
                            cell.classList.add('positive');
                        }}
                    }} else if (text.startsWith('-')) {{
                        cell.classList.add('negative');
                    }} else if (text.startsWith('+')) {{
                        cell.classList.add('positive');
                    }}
                }}
            }});
        }});
    </script>
</body>
</html>""".format(
        css_style=css_style,
        username_display=username_display,
        market_content=market_content,
    )
    return html


def get_portfolio_page_html(
    fund_content, fund_map, market_charts=None, chart_data=None, username=None
):
    """生成持仓基金页面"""
    css_style = get_css_style()
    import json

    username_display = ""
    if username:
        username_display = '<span class="nav-user"><i class="ri-user-smile-line"></i> {username}</span>'.format(
            username=username
        )
        username_display += '<a href="/logout" class="nav-logout">退出登录</a>'

    # 准备图表数据JSON
    timing_data_json = json.dumps(
        chart_data.get("timing", {"labels": [], "prices": [], "volumes": []})
        if chart_data
        else {"labels": [], "prices": [], "volumes": []}
    )

    # 生成市场图表HTML - 只保留上证分时
    market_charts_html = """
        <!-- 市场指数区域 -->
        <div class="market-charts-section" style="margin-bottom: 30px;">
            <!-- 上证分时 - 单独一行，使用Chart.js -->
            <div class="chart-card" style="background-color: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; overflow: hidden;">
                <div class="chart-card-header" style="padding: 12px 15px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center;">
                    <h3 id="timingChartTitle" style="margin: 0; font-size: 1rem; color: var(--text-main);"><i class="ri-time-line"></i> 上证分时</h3>
                </div>
                <div class="chart-card-content" style="padding: 15px; height: 180px;">
                    <canvas id="timingChart"></canvas>
                </div>
            </div>
        </div>
    """

    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>持仓基金 - LanFund</title>
    <link rel="icon" href="/static/1.ico">
    {css_style}
    <link rel="stylesheet" href="/static/css/style.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        body {{
            background-color: var(--terminal-bg);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}

        /* 顶部导航栏 */
        .top-navbar {{
            background-color: var(--card-bg);
            color: var(--text-main);
            padding: 0.8rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
        }}

        .top-navbar-brand {{
            display: flex;
            align-items: center;
            flex: 0 0 auto;
        }}

        .top-navbar-quote {{
            flex: 1;
            text-align: center;
            font-size: 1rem;
            font-weight: 500;
            color: var(--text-main);
            font-style: italic;
            padding: 0 2rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            letter-spacing: 0.05em;
            transition: opacity 0.5s ease-in-out;
        }}

        .top-navbar-menu {{
            display: flex;
            gap: 1rem;
            align-items: center;
        }}

        .nav-user {{
            color: #3b82f6;
            font-weight: 500;
        }}

        .nav-logout {{
            color: #f85149;
            text-decoration: none;
            font-weight: 500;
        }}

        /* 主容器 */
        .main-container {{
            display: flex;
            flex: 1;
        }}

        /* 内容区域 */
        .content-area {{
            flex: 1;
            padding: 30px;
            overflow-y: auto;
        }}

        .portfolio-header {{
            margin-bottom: 20px;
        }}

        .portfolio-header h1 {{
            font-size: 1.5rem;
            font-weight: 600;
            margin: 0;
            color: var(--text-main);
        }}

        .portfolio-header p {{
            color: var(--text-dim);
            margin: 5px 0 0;
            font-size: 0.9rem;
        }}

        .operations-panel {{
            background: rgba(102, 126, 234, 0.05);
            border: 1px solid rgba(102, 126, 234, 0.1);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 30px;
        }}

        .operation-group {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}

        .fund-content {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
        }}

        @media (max-width: 768px) {{
            .main-container {{
                flex-direction: column;
            }}

            .sidebar {{
                width: 100%;
                border-right: none;
                border-bottom: 1px solid var(--border);
                padding: 10px 0;
            }}

            .sidebar-item {{
                padding: 10px 15px;
                font-size: 0.9rem;
            }}

            .content-area {{
                padding: 15px;
            }}

            .top-navbar {{
                padding: 0.6rem 1rem;
            }}

            .top-navbar-quote {{
                font-size: 0.75rem;
                padding: 0 0.5rem;
            }}

            .market-charts-grid {{
                grid-template-columns: 1fr;
            }}

            .chart-card-content {{
                max-height: 250px;
            }}
        }}

        @media (max-width: 1024px) {{
            .market-charts-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <!-- 顶部导航栏 -->
    <nav class="top-navbar">
        <div class="top-navbar-brand">
            <img src="/static/1.ico" alt="Logo" class="navbar-logo">
        </div>
        <div class="top-navbar-quote" id="lyricsDisplay">
            偶然与巧合, 舞动了蝶翼, 谁的心头风起 ————《如果我们不曾相遇》
        </div>
        <div class="top-navbar-menu">
            {username_display}
        </div>
    </nav>

    <!-- 主容器 -->
    <div class="main-container">
        <!-- 左侧导航栏 -->
        <div class="sidebar collapsed" id="sidebar">
            <div class="sidebar-toggle" id="sidebarToggle"><i class="ri-arrow-right-s-line"></i></div>
            <a href="/market" class="sidebar-item">
                <span class="sidebar-icon"><i class="ri-newspaper-line"></i></span>
                <span>7*24快讯</span>
            </a>
            <a href="/market-indices" class="sidebar-item">
                <span class="sidebar-icon"><i class="ri-bar-chart-2-line"></i></span>
                <span>市场指数</span>
            </a>
            <a href="/precious-metals" class="sidebar-item">
                <span class="sidebar-icon">🪙</span>
                <span>贵金属行情</span>
            </a>
            <a href="/portfolio" class="sidebar-item active">
                <span class="sidebar-icon"><i class="ri-briefcase-4-line"></i></span>
                <span>持仓基金</span>
            </a>
            <a href="/sectors" class="sidebar-item">
                <span class="sidebar-icon"><i class="ri-building-4-line"></i></span>
                <span>行业板块</span>
            </a>
        </div>

        <!-- 内容区域 -->
        <div class="content-area">
            <!-- 页面标题 -->
            <div class="portfolio-header">
                <h1>
                    <i class="ri-briefcase-4-line"></i> 持仓基金
                    <button id="refreshBtn" onclick="refreshCurrentPage()" class="refresh-button">🔄 刷新</button>
                </h1>
            </div>

            <!-- Refresh button styling -->
            <style>
                .refresh-button {{
                    margin-left: 15px;
                    padding: 8px 16px;
                    background: var(--accent);
                    color: white;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 0.9rem;
                    font-weight: 500;
                    transition: all 0.2s ease;
                    display: inline-flex;
                    align-items: center;
                    gap: 5px;
                }}
                .refresh-button:hover {{
                    background: #2563eb;
                    transform: translateY(-1px);
                }}
                .refresh-button:disabled {{
                    background: #6b7280;
                    cursor: not-allowed;
                    transform: none;
                }}
                .portfolio-header h1 {{
                    display: flex;
                    align-items: center;
                }}
            </style>

            <!-- 免责声明 -->
            <div style="margin-bottom: 20px; padding: 12px 15px; background: rgba(255, 193, 7, 0.1); border: 1px solid rgba(255, 193, 7, 0.3); border-radius: 8px; font-size: 0.85rem; color: var(--text-dim);">
                <p style="margin: 0; line-height: 1.5;">
                    <strong style="color: #ffc107;"><i class="ri-alert-line"></i> 免责声明</strong>：
                    预估收益根据您输入的持仓份额与实时估值计算得出，仅供参考。
                    实际收益以基金公司最终结算为准，可能因份额确认时间、分红方式、费用扣除等因素存在偏差。
                    投资有风险，入市需谨慎。
                </p>
            </div>

            <!-- 市场图表 (上证分时) -->
            {market_charts_html}

            <!-- 基金内容 -->
            <div class="fund-content">
                {fund_content}
            </div>
        </div>
    </div>

    <!-- Modals (复用现有模态框) -->
    <div class="sector-modal" id="sectorModal">
        <div class="sector-modal-content">
            <div class="sector-modal-header">选择板块</div>
            <input type="text" class="sector-modal-search" id="sectorSearch" placeholder="搜索板块名称...">
            <div id="sectorCategories"></div>
            <div class="sector-modal-footer">
                <button class="btn btn-secondary" onclick="closeSectorModal()">取消</button>
                <button class="btn btn-primary" onclick="confirmSector()">确定</button>
            </div>
        </div>
    </div>

    <div class="sector-modal" id="fundSelectionModal">
        <div class="sector-modal-content">
            <div class="sector-modal-header" id="fundSelectionTitle">选择基金</div>
            <input type="text" class="sector-modal-search" id="fundSelectionSearch" placeholder="搜索基金代码或名称...">
            <div id="fundSelectionList" style="max-height: 400px; overflow-y: auto;"></div>
            <div class="sector-modal-footer">
                <button class="btn btn-secondary" onclick="closeFundSelectionModal()">取消</button>
                <button class="btn btn-primary" id="fundSelectionConfirmBtn" onclick="confirmFundSelection()">确定</button>
            </div>
        </div>
    </div>

    <div class="confirm-dialog" id="confirmDialog">
        <div class="confirm-dialog-content">
            <h3 id="confirmTitle" class="confirm-title"></h3>
            <p id="confirmMessage" class="confirm-message"></p>
            <div class="confirm-actions">
                <button class="btn btn-secondary" onclick="closeConfirmDialog()">取消</button>
                <button class="btn btn-primary" id="confirmBtn">确定</button>
            </div>
        </div>
    </div>

    <!-- 份额设置弹窗 -->
    <div class="sector-modal" id="sharesModal">
        <div class="sector-modal-content" style="max-width: 400px;">
            <div class="sector-modal-header">设置持仓份额</div>
            <div style="padding: 20px;">
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 8px; color: var(--text-main); font-weight: 500;">基金代码</label>
                    <div id="sharesModalFundCode" style="padding: 10px; background: rgba(59, 130, 246, 0.1); border-radius: 6px; color: #3b82f6; font-weight: 600; font-family: monospace;"></div>
                </div>
                <div style="margin-bottom: 15px;">
                    <label for="sharesModalInput" style="display: block; margin-bottom: 8px; color: var(--text-main); font-weight: 500;">持仓份额</label>
                    <input type="number" id="sharesModalInput" step="0.01" min="0" placeholder="请输入份额"
                           style="width: 100%; padding: 10px 12px; border: 1px solid var(--border); border-radius: 6px; font-size: 14px; background: var(--card-bg); color: var(--text-main);">
                </div>
            </div>
            <div class="sector-modal-footer">
                <button class="btn btn-secondary" onclick="closeSharesModal()">取消</button>
                <button class="btn btn-primary" onclick="confirmShares()">确定</button>
            </div>
        </div>
    </div>

    <script src="/static/js/main.js"></script>
    <script>
        // 上证分时数据
        const timingData = {timing_data_json};

        document.addEventListener('DOMContentLoaded', function() {{
            // 自动颜色化
            const cells = document.querySelectorAll('.style-table td');
            cells.forEach(cell => {{
                const text = cell.textContent.trim();
                const cleanText = text.replace(/[%,亿万手]/g, '');
                const val = parseFloat(cleanText);

                if (!isNaN(val)) {{
                    if (text.includes('%') || text.includes('涨跌')) {{
                        if (text.includes('-')) {{
                            cell.classList.add('negative');
                        }} else if (val > 0) {{
                            cell.classList.add('positive');
                        }}
                    }} else if (text.startsWith('-')) {{
                        cell.classList.add('negative');
                    }} else if (text.startsWith('+')) {{
                        cell.classList.add('positive');
                    }}
                }}
            }});

            // 歌词轮播
            const lyrics = [
                '总要有一首我的歌, 大声唱过, 再看天地辽阔 ————《一颗苹果》',
                '苍狗又白云, 身旁有了你, 匆匆轮回又有何惧 ————《如果我们不曾相遇》',
                '活着其实很好, 再吃一颗苹果 ————《一颗苹果》',
                '偶然与巧合, 舞动了蝶翼, 谁的心头风起 ————《如果我们不曾相遇》'
            ];
            let currentLyricIndex = 0;
            const lyricsElement = document.getElementById('lyricsDisplay');

            // 随机选择初始歌词
            currentLyricIndex = Math.floor(Math.random() * lyrics.length);
            if (lyricsElement) {{
                lyricsElement.textContent = lyrics[currentLyricIndex];

                // 每10秒切换一次歌词
                setInterval(function() {{
                    // 淡出
                    lyricsElement.style.opacity = '0';

                    setTimeout(function() {{
                        // 切换歌词
                        currentLyricIndex = (currentLyricIndex + 1) % lyrics.length;
                        lyricsElement.textContent = lyrics[currentLyricIndex];

                        // 淡入
                        lyricsElement.style.opacity = '1';
                    }}, 500);
                }}, 10000);
            }}

            // 初始化上证分时图表
            initTimingChart();
        }});

                        // 上证分时图表 - 使用API返回的实际涨跌幅
        function initTimingChart() {{
            const ctx = document.getElementById('timingChart');
            if (!ctx || timingData.labels.length === 0) return;

            // 使用API返回的实际数据（已经处理好的）
            const changePercentages = timingData.change_pcts || [];
            const changeAmounts = timingData.change_amounts || [];  // 原始涨跌额数据
            const basePrice = timingData.prices[0];
            const lastPrice = timingData.prices[timingData.prices.length - 1];

            // 使用最后一个实际涨跌幅值
            const lastPct = changePercentages.length > 0 ? changePercentages[changePercentages.length - 1] : 0;
            const titleColor = lastPct >= 0 ? '#f44336' : '#4caf50';

            // 更新标题颜色 - 现在主要显示实际涨跌幅
            const titleElement = document.getElementById('timingChartTitle');
            if (titleElement) {{
                titleElement.style.color = titleColor;
                titleElement.innerHTML = '<i class="ri-time-line"></i> 上证分时 <span style="font-size:0.9em;">' +
                    (lastPct >= 0 ? '+' : '') + lastPct.toFixed(2) + '% (' + lastPrice.toFixed(2) + ')</span>';
            }}

            // 保存图表实例到全局变量，方便后续更新
            window.timingChartInstance = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: timingData.labels,
                    datasets: [{{
                        label: '涨跌幅 (%)',
                        data: changePercentages,
                        borderColor: function(context) {{
                            // 动态返回颜色：>0% 红色，<0% 绿色，=0% 灰色
                            const index = context.dataIndex;
                            if (index === undefined || index < 0) return '#9ca3af';
                            const pct = changePercentages[index];
                            return pct > 0 ? '#f44336' : (pct < 0 ? '#4caf50' : '#9ca3af');
                        }},
                        segment: {{
                            borderColor: function(context) {{
                                // 根据线段的结束点判断颜色
                                const pct = changePercentages[context.p1DataIndex];
                                return pct > 0 ? '#f44336' : (pct < 0 ? '#4caf50' : '#9ca3af');
                            }}
                        }},
                        backgroundColor: function(context) {{
                            const chart = context.chart;
                            const {{ctx, chartArea}} = chart;
                            if (!chartArea) return null;
                            // 根据当前最新涨跌幅判断整体涨跌来设置背景色
                            const lastPct = changePercentages[changePercentages.length - 1];
                            const color = lastPct >= 0 ? '244, 67, 54' : '76, 175, 80';
                            const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
                            gradient.addColorStop(0, 'rgba(' + color + ', 0.2)');
                            gradient.addColorStop(1, 'rgba(' + color + ', 0.0)');
                            return gradient;
                        }},
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0,
                        pointHoverRadius: 4,
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {{
                        mode: 'index',
                        intersect: false,
                    }},
                    plugins: {{
                        legend: {{
                            display: true,
                            position: 'top',
                            labels: {{
                                font: {{ size: 11 }},
                                boxWidth: 12,
                                generateLabels: function(chart) {{
                                    const lastPct = changePercentages[changePercentages.length - 1];
                                    const color = lastPct >= 0 ? '#ff4d4f' : '#52c41a';
                                    return [{{
                                        text: '涨跌幅: ' + (lastPct >= 0 ? '+' : '') + lastPct.toFixed(2) + '% (' + lastPrice.toFixed(2) + ')',
                                        fillStyle: color,
                                        strokeStyle: color,
                                        fontColor: color,
                                        lineWidth: 2,
                                        hidden: false,
                                        index: 0
                                    }}];
                                }}
                            }}
                        }},
                        tooltip: {{
                            callbacks: {{
                                title: function(context) {{
                                    return '时间: ' + context[0].label;
                                }},
                                label: function(context) {{
                                    const index = context.dataIndex;
                                    const pct = changePercentages[index];
                                    const price = timingData.prices[index];
                                    const changeAmt = changeAmounts[index];  // 使用原始涨跌额数据
                                    const volume = timingData.volumes ? timingData.volumes[index] : 0;
                                    const amount = timingData.amounts ? timingData.amounts[index] : 0;
                                    return [
                                        '涨跌幅: ' + (pct >= 0 ? '+' : '') + pct.toFixed(2) + '%',
                                        '上证指数: ' + price.toFixed(2),
                                        '涨跌额: ' + (changeAmt >= 0 ? '+' : '') + changeAmt.toFixed(2),
                                        '成交量: ' + volume.toFixed(0) + '万手',
                                        '成交额: ' + amount.toFixed(2) + '亿'
                                    ];
                                }}
                            }}
                        }},
                        datalabels: {{
                            display: false
                        }}
                    }},
                    scales: {{
                        x: {{
                            ticks: {{
                                color: '#9ca3af',
                                font: {{ size: 10 }},
                                maxTicksLimit: 6
                            }},
                            grid: {{
                                color: 'rgba(255, 255, 255, 0.1)'
                            }}
                        }},
                        y: {{
                            title: {{
                                display: true,
                                text: '涨跌幅 (%)',
                                color: '#9ca3af',
                                font: {{ size: 11 }}
                            }},
                            ticks: {{
                                color: '#9ca3af',
                                callback: function(value) {{
                                    return (value >= 0 ? '+' : '') + value.toFixed(2) + '%';
                                }}
                            }},
                            grid: {{
                                color: 'rgba(255, 255, 255, 0.1)'
                            }}
                        }}
                    }}
                }}
            }});
        }}
    </script>
</body>
</html>""".format(
        css_style=css_style,
        username_display=username_display,
        market_charts_html=market_charts_html,
        fund_content=fund_content,
        timing_data_json=timing_data_json,
    )
    return html


def get_market_icon(key):
    """获取市场数据的图标"""
    icons = {
        "kx": '<i class="ri-newspaper-line"></i>',
        "marker": '<i class="ri-earth-line"></i>',
        "real_time_gold": '<i class="ri-vip-diamond-line"></i>',
        "gold": '<i class="ri-line-chart-line"></i>',
        "seven_A": '<i class="ri-bar-chart-grouped-line"></i>',
        "A": '<i class="ri-bar-chart-box-line"></i>',
        "bk": '<i class="ri-building-4-line"></i>',
        "select_fund": '<i class="ri-search-2-line"></i>',
    }
    return icons.get(key, '<i class="ri-bar-chart-2-line"></i>')


def get_sectors_page_html(
    sectors_content, select_fund_content, fund_map, username=None
):
    """生成行业板块基金查询页面"""
    css_style = get_css_style()

    username_display = ""
    if username:
        username_display = '<span class="nav-user"><i class="ri-user-smile-line"></i> {username}</span>'.format(
            username=username
        )
        username_display += '<a href="/logout" class="nav-logout">退出登录</a>'

    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>行业板块 - LanFund</title>
    <link rel="icon" href="/static/1.ico">
    {css_style}
    <link rel="stylesheet" href="/static/css/style.css">
    <style>
        body {{
            background-color: var(--terminal-bg);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}

        /* 顶部导航栏 */
        .top-navbar {{
            background-color: var(--card-bg);
            color: var(--text-main);
            padding: 0.8rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
        }}

        .top-navbar-brand {{
            display: flex;
            align-items: center;
            flex: 0 0 auto;
        }}

        .top-navbar-quote {{
            flex: 1;
            text-align: center;
            font-size: 1rem;
            font-weight: 500;
            color: var(--text-main);
            font-style: italic;
            padding: 0 2rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            letter-spacing: 0.05em;
            transition: opacity 0.5s ease-in-out;
        }}

        .top-navbar-menu {{
            display: flex;
            gap: 1rem;
            align-items: center;
        }}

        .nav-user {{
            color: #3b82f6;
            font-weight: 500;
        }}

        .nav-logout {{
            color: #f85149;
            text-decoration: none;
            font-weight: 500;
        }}

        /* 主容器 */
        .main-container {{
            display: flex;
            flex: 1;
        }}

        /* 内容区域 */
        .content-area {{
            flex: 1;
            padding: 30px;
            overflow-y: auto;
        }}

        /* 隐藏滚动条但保留功能 */
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}

        ::-webkit-scrollbar-track {{
            background: transparent;
        }}

        ::-webkit-scrollbar-thumb {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: rgba(255, 255, 255, 0.2);
        }}

        /* Firefox */
        * {{
            scrollbar-width: thin;
            scrollbar-color: rgba(255, 255, 255, 0.1) transparent;
        }}

        .page-header {{
            margin-bottom: 30px;
        }}

        .page-header h1 {{
            font-size: 2rem;
            font-weight: 700;
            margin: 0;
            color: var(--text-main);
            border: none;
            text-decoration: none;
        }}

        .page-header p {{
            color: var(--text-dim);
            margin-top: 10px;
            border: none;
            text-decoration: none;
        }}

        /* Tab 内容 */
        .tab-content {{
            display: none;
        }}

        .tab-content.active {{
            display: block;
        }}

        .content-card {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
        }}

        /* Tab 切换按钮 */
        .tab-button {{
            padding: 10px 20px;
            background: none;
            border: none;
            color: var(--text-dim);
            cursor: pointer;
            font-size: 1rem;
            font-weight: 500;
            transition: all 0.2s ease;
        }}

        .tab-button:hover {{
            color: var(--text-main);
        }}

        .tab-button.active {{
            color: var(--accent);
        }}

        @media (max-width: 768px) {{
            .main-container {{
                flex-direction: column;
            }}

            .sidebar {{
                width: 100%;
                border-right: none;
                border-bottom: 1px solid var(--border);
                padding: 10px 0;
            }}

            .sidebar-item {{
                padding: 10px 15px;
                font-size: 0.9rem;
            }}

            .content-area {{
                padding: 15px;
            }}

            .top-navbar {{
                padding: 0.6rem 1rem;
            }}

            .top-navbar-quote {{
                font-size: 0.75rem;
                padding: 0 0.5rem;
            }}
        }}
    </style>
</head>
<body>
    <!-- 顶部导航栏 -->
    <nav class="top-navbar">
        <div class="top-navbar-brand">
            <img src="/static/1.ico" alt="Logo" class="navbar-logo">
        </div>
        <div class="top-navbar-quote" id="lyricsDisplay">
            偶然与巧合, 舞动了蝶翼, 谁的心头风起 ————《如果我们不曾相遇》
        </div>
        <div class="top-navbar-menu">
            {username_display}
        </div>
    </nav>

    <!-- 主容器 -->
    <div class="main-container">
        <!-- 左侧导航栏 -->
        <div class="sidebar collapsed" id="sidebar">
            <div class="sidebar-toggle" id="sidebarToggle"><i class="ri-arrow-right-s-line"></i></div>
            <a href="/market" class="sidebar-item">
                <span class="sidebar-icon"><i class="ri-newspaper-line"></i></span>
                <span>7*24快讯</span>
            </a>
            <a href="/market-indices" class="sidebar-item">
                <span class="sidebar-icon"><i class="ri-bar-chart-2-line"></i></span>
                <span>市场指数</span>
            </a>
            <a href="/precious-metals" class="sidebar-item">
                <span class="sidebar-icon">🪙</span>
                <span>贵金属行情</span>
            </a>
            <a href="/portfolio" class="sidebar-item">
                <span class="sidebar-icon"><i class="ri-briefcase-4-line"></i></span>
                <span>持仓基金</span>
            </a>
            <a href="/sectors" class="sidebar-item active">
                <span class="sidebar-icon"><i class="ri-building-4-line"></i></span>
                <span>行业板块</span>
            </a>
        </div>

        <!-- 内容区域 -->
        <div class="content-area">
            <!-- Tab 切换按钮 -->
            <div class="tab-buttons" style="display: flex; gap: 10px; margin-bottom: 20px;">
                <button class="tab-button active" onclick="switchTab('sectors')" id="tab-btn-sectors">
                    <i class="ri-building-4-line"></i> 行业板块
                </button>
                <button class="tab-button" onclick="switchTab('query')" id="tab-btn-query">
                    <i class="ri-search-2-line"></i> 板块基金查询
                </button>
            </div>

            <!-- 行业板块 Tab -->
            <div id="tab-sectors" class="tab-content active">
                <div class="page-header">
                    <h1 style="display: flex; align-items: center;">
                        <i class="ri-building-4-line"></i> 行业板块
                        <button id="refreshBtn" onclick="refreshCurrentPage()" class="refresh-button" style="margin-left: 15px; padding: 8px 16px; background: var(--accent); color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-weight: 500; transition: all 0.2s ease; display: inline-flex; align-items: center; gap: 5px;">🔄 刷新</button>
                    </h1>
                    <p>查看各行业板块的市场表现</p>
                </div>
                <div class="content-card">
                    {sectors_content}
                </div>
            </div>

            <!-- 板块基金查询 Tab -->
            <div id="tab-query" class="tab-content">
                <div class="page-header">
                    <h1 style="display: flex; align-items: center;">
                        <i class="ri-search-2-line"></i> 板块基金查询
                        <button id="refreshBtn" onclick="refreshCurrentPage()" class="refresh-button" style="margin-left: 15px; padding: 8px 16px; background: var(--accent); color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-weight: 500; transition: all 0.2s ease; display: inline-flex; align-items: center; gap: 5px;">🔄 刷新</button>
                    </h1>
                    <p>查询特定板块的基金产品</p>
                </div>
                <div class="content-card">
                    {select_fund_content}
                </div>
            </div>
        </div>
    </div>

    <script src="/static/js/main.js"></script>
    <script src="/static/js/sidebar-nav.js"></script>
    <script>
        function switchTab(tabName) {{
            // 隐藏所有 tab 内容
            document.querySelectorAll('.tab-content').forEach(tab => {{
                tab.classList.remove('active');
            }});

            // 移除所有 tab 按钮的 active 状态
            document.querySelectorAll('.tab-button').forEach(btn => {{
                btn.classList.remove('active');
            }});

            // 显示选中的 tab
            document.getElementById('tab-' + tabName).classList.add('active');

            // 设置对应 tab 按钮为 active
            document.getElementById('tab-btn-' + tabName).classList.add('active');
        }}

        // 自动颜色化函数
        function autoColorize() {{
            const cells = document.querySelectorAll('.style-table td');
            cells.forEach(cell => {{
                const text = cell.textContent.trim();
                const cleanText = text.replace(/[%,亿万手]/g, '');
                const val = parseFloat(cleanText);

                if (!isNaN(val)) {{
                    if (text.includes('%') || text.includes('涨跌')) {{
                        if (text.includes('-')) {{
                            cell.classList.add('negative');
                        }} else if (val > 0) {{
                            cell.classList.add('positive');
                        }}
                    }} else if (text.startsWith('-')) {{
                        cell.classList.add('negative');
                    }} else if (text.startsWith('+')) {{
                        cell.classList.add('positive');
                    }}
                }}
            }});
        }}

        // 默认激活第一个 tab
        document.addEventListener('DOMContentLoaded', function() {{
            const firstTabBtn = document.querySelector('.tab-button');
            if (firstTabBtn) {{
                firstTabBtn.classList.add('active');
            }}

            // 歌词轮播
            const lyrics = [
                '总要有一首我的歌, 大声唱过, 再看天地辽阔 ————《一颗苹果》',
                '苍狗又白云, 身旁有了你, 匆匆轮回又有何惧 ————《如果我们不曾相遇》',
                '活着其实很好, 再吃一颗苹果 ————《一颗苹果》',
                '偶然与巧合, 舞动了蝶翼, 谁的心头风起 ————《如果我们不曾相遇》'
            ];
            let currentLyricIndex = 0;
            const lyricsElement = document.getElementById('lyricsDisplay');

            // 随机选择初始歌词
            currentLyricIndex = Math.floor(Math.random() * lyrics.length);
            if (lyricsElement) {{
                lyricsElement.textContent = lyrics[currentLyricIndex];

                // 每10秒切换一次歌词
                setInterval(function() {{
                    // 淡出
                    lyricsElement.style.opacity = '0';

                    setTimeout(function() {{
                        // 切换歌词
                        currentLyricIndex = (currentLyricIndex + 1) % lyrics.length;
                        lyricsElement.textContent = lyrics[currentLyricIndex];

                        // 淡入
                        lyricsElement.style.opacity = '1';
                    }}, 500);
                }}, 10000);
            }}

            // 自动颜色化
            autoColorize();
        }});
    </script>
</body>
</html>""".format(
        css_style=css_style,
        username_display=username_display,
        sectors_content=sectors_content,
        select_fund_content=select_fund_content,
    )
    return html
