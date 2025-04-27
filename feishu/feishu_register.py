import asyncio
from playwright.async_api import async_playwright, Page # Import Page type hint
import time

async def get_template_auth_code(page: Page, template_url: str) -> str:
    """导航到模板，使用模板，并获取多维表格授权码。"""
    print(f"导航到模板链接: {template_url}")
    await page.goto(template_url)
    await page.wait_for_load_state('networkidle')
    print("模板页面加载完成")

    # 等待并点击“使用该模板”按钮
    use_template_button_selector = 'button.preview-footer__use-btn:has-text("使用该模板")'
    print(f"等待并点击 '{use_template_button_selector}' 按钮")
    auth_token = ""
    try:
        use_template_button = page.locator(use_template_button_selector)
        await use_template_button.wait_for(state='visible', timeout=15000) # 增加等待时间

        # 监听新页面事件
        async with page.context.expect_page() as new_page_info:
            await use_template_button.click()
            print("已点击 '使用该模板' 按钮")

        new_page = await new_page_info.value
        await new_page.wait_for_load_state('networkidle')
        new_page_url = new_page.url
        print(f"已切换到新页面，URL: {new_page_url}")
        # TODO: 保存 new_page_url 到需要的地方

        # 在新页面上操作
        page = new_page # 将后续操作的目标页面切换为新页面

    except Exception as e:
        print(f"点击 '使用该模板' 按钮或切换页面时出错: {e}")
        await page.screenshot(path="error_use_template.png")
        raise # 抛出异常，中断后续流程
    # 页面刷新一下
    print("页面刷新中...")
    await page.reload()
    print("页面已刷新")
    # 点击多维表格插件按钮
    plugin_button_selector = 'div.pc-tools button:has(svg[data-icon="BasePlugInOutlined"])' # 使用用户提供的正确选择器
    print(f"等待并点击多维表格插件按钮: {plugin_button_selector}")
    try:
        plugin_button = page.locator(plugin_button_selector)
        await plugin_button.wait_for(state='visible', timeout=10000)
        await plugin_button.click()
        print("已点击多维表格插件按钮")
    except Exception as e:
        print(f"点击多维表格插件按钮时出错: {e}")
        await page.screenshot(path="error_plugin_button.png")
        raise # 抛出异常，中断后续流程

    # 点击自定义插件按钮
    custom_plugin_button_selector = 'button.custom-button:has-text("自定义插件")'
    print(f"等待并点击自定义插件按钮: {custom_plugin_button_selector}")
    try:
        custom_plugin_button = page.locator(custom_plugin_button_selector)
        await custom_plugin_button.wait_for(state='visible', timeout=10000)
        await custom_plugin_button.click()
        print("已点击自定义插件按钮")
    except Exception as e:
        print(f"点击自定义插件按钮时出错: {e}")
        await page.screenshot(path="error_custom_plugin_button.png")
        raise

    # 点击获取授权码
    get_token_link_selector = 'span.extension-market-link-btn-v4:has-text("获取授权码")'
    print(f"等待并点击获取授权码链接: {get_token_link_selector}")
    try:
        get_token_link = page.locator(get_token_link_selector)
        await get_token_link.wait_for(state='visible', timeout=10000)
        await get_token_link.click()
        print("已点击获取授权码")
    except Exception as e:
        print(f"点击获取授权码时出错: {e}")
        await page.screenshot(path="error_get_token_link.png")
        raise

    # 处理授权码弹窗
    print("等待授权码弹窗出现...")
    token_modal_selector = 'div.ud__modal__content:has-text("多维表格授权码")' # 定位弹窗
    try:
        await page.locator(token_modal_selector).wait_for(state='visible', timeout=10000)
        print("授权码弹窗已出现")

        # 确认启用授权码已勾选 (根据截图，默认是勾选的，可以加个检查)
        enable_checkbox_selector = 'label.open-extension-container__personal-token__checkbox input[type="checkbox"]'
        while True:
            try:
                print(f"尝试定位并检查/勾选复选框: {enable_checkbox_selector}")
                is_checked = await page.locator(enable_checkbox_selector).is_checked(timeout=5000) # 缩短超时
                if not is_checked:
                    print("启用授权码未勾选，尝试勾选...")
                    await page.locator(enable_checkbox_selector).check()
                    print("已勾选启用授权码")
                else:
                    print("启用授权码已勾选")
                break # 成功则跳出循环
            except Exception as e:
                print(f"定位或操作复选框 '{enable_checkbox_selector}' 失败: {e}")
                await page.screenshot(path="error_checkbox_debug.png")
                print("已保存调试截图: error_checkbox_debug.png")
                new_selector = input("请输入新的复选框CSS选择器 (或按Enter跳过勾选): ").strip()
                if not new_selector:
                    print("跳过复选框操作。")
                    break # 用户选择跳过
                enable_checkbox_selector = new_selector # 更新选择器并重试

        # 获取授权码文本
        token_input_selector = 'div.open-extension-container__personal-token__content-token-input'
        auth_token = await page.locator(token_input_selector).inner_text()
        print(f"获取到的授权码: {auth_token}")

        # 点击复制按钮 (可选)
        copy_button_selector = f'{token_modal_selector} button:has-text("复制")'
        print(f"点击复制按钮: {copy_button_selector}")
        await page.locator(copy_button_selector).click()
        print("已点击复制按钮")

        # 点击确定按钮
        confirm_button_selector = f'{token_modal_selector} button:has-text("确定")'
        print(f"点击确定按钮: {confirm_button_selector}")
        await page.locator(confirm_button_selector).click()
        print("已点击确定按钮，关闭弹窗")

    except Exception as e:
        print(f"处理授权码弹窗时出错: {e}")
        await page.screenshot(path="error_token_modal.png")
        raise

    return auth_token

async def register_feishu(phone_number):
    async with async_playwright() as p:
        # 启动浏览器，可以指定浏览器类型，如 chromium, firefox, webkit
        # headless=False 表示显示浏览器界面，方便调试
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            # 访问飞书注册页面
            print("正在访问飞书注册页面...")
            await page.goto("https://www.feishu.cn/create/")

            # 等待页面加载完成，可以根据实际情况调整等待时间或使用更精确的等待条件
            await page.wait_for_load_state('networkidle')
            print("页面加载完成")

            # --- 设置企业信息 ---
            print("正在设置企业信息...")
            # 填写公司/团队名称
            company_name_input_selector = 'input#register_team_name' # 根据HTML更新的选择器
            print(f"正在定位公司名称输入框: {company_name_input_selector}")
            await page.locator(company_name_input_selector).fill("时间管理")
            print("已输入公司名称: 时间管理")

            # 选择行业（教育） - 两级下拉菜单
            industry_dropdown_selector = 'input[placeholder="请选择行业类型"]'
            # 假设第一级和第二级选项都使用 '教育' 文本，并且出现在弹出层中
            # 注意：这些选择器可能需要根据实际页面结构微调
            # 更新选择器以定位 #pp_popupContainer 内的元素
            popup_container_selector = "#pp_popupContainer"
            # 第一级行业选项选择器 (例如 '教育')
            first_level_industry_option_selector = f"{popup_container_selector} .drop_down-options-cascader >> li:has(div.overflow-tip-content:text('教育'))"
            # 第二级行业选项选择器 (例如 '教育') - 注意: nth=1 选择第二个列表
            second_level_industry_option_selector = f"{popup_container_selector} .drop_down-options-cascader >> nth=1 >> li:has(div.overflow-tip-content:text('教育'))"

            print(f"正在点击行业类型下拉菜单")
            await page.locator(industry_dropdown_selector).click() # 点击打开下拉菜单
            
            # 等待并点击第一级行业选项
            print(f"等待第一级行业选项 '{first_level_industry_option_selector}' 可见")
            first_level_option = page.locator(first_level_industry_option_selector).first
            await first_level_option.wait_for(state='visible', timeout=5000)
            print(f"正在选择第一级行业: 教育")
            await first_level_option.click()
            
            # 增加等待时间确保第二级菜单加载
            await page.wait_for_timeout(1500) # 可根据实际情况调整

            print(f"正在选择第二级行业: 教育")
            # 尝试定位并点击第二级选项
            print(f"使用选择器定位第二级选项: {second_level_industry_option_selector}")
            second_level_option = page.locator(second_level_industry_option_selector).first
            try:
                print("等待第二级选项可见...")
                await second_level_option.wait_for(state='visible', timeout=5000) # 等待第二级可见
                print("第二级选项可见，尝试点击...")
                await second_level_option.click()
                print("已点击第二级选项")
            except Exception as e:
                print(f"选择第二级行业失败（选择器: {second_level_industry_option_selector}）: {e}")
                # 可以选择在这里停止或继续执行其他操作
            print("已选择行业: 教育 -> 教育")

            # 选择规模（1-9 人） - 更新选择器以定位 #pp_popupContainer 内的元素
            size_dropdown_selector = 'input[placeholder="选择人员规模"]'
            # 假设规模选项也在 #pp_popupContainer 中
            size_option_selector = f"{popup_container_selector} li:has-text('1-9 人')"
            print(f"正在选择规模: 1-9 人")
            await page.locator(size_dropdown_selector).click() # 点击打开下拉菜单
            # 等待规模选项可见
            print(f"等待规模选项 '{size_option_selector}' 可见")
            size_option = page.locator(size_option_selector).first
            await size_option.wait_for(state='visible', timeout=5000)
            await size_option.click() # 点击选择选项
            print("已选择规模: 1-9 人")

            # 点击下一步按钮
            next_button_selector = 'button.enter-team-info-next-button:has-text("下一步")' # 根据HTML更新的选择器
            print(f"正在点击下一步按钮: {next_button_selector}")
            await page.locator(next_button_selector).click()
            print("已点击下一步")
            
            # --- 设置个人信息 --- 
            print("等待设置个人信息页面加载...")
            # 等待一个明确的元素出现，例如手机号输入框
            personal_info_phone_selector = 'input[placeholder="请输入你的手机号"]'
            await page.locator(personal_info_phone_selector).wait_for(state='visible', timeout=10000)
            print("设置个人信息页面加载完成")

            # 填写手机号
            print(f"正在定位手机号输入框: {personal_info_phone_selector}")
            await page.locator(personal_info_phone_selector).fill("18580269254")
            print("已输入手机号: 18580269254")

            # 填写姓名
            name_input_selector = 'input[placeholder="请输入你的姓名"]'
            print(f"正在定位姓名输入框: {name_input_selector}")
            await page.locator(name_input_selector).fill("时间管理")
            print("已输入姓名: 时间管理")

            # 勾选同意协议
            # 尝试使用更精确的选择器定位复选框
            agreement_checkbox_selector = 'label.ud__checkbox__wrapper input.ud__checkbox__input' # 使用用户提供的HTML结构更新选择器
            # 备用选择器（如果上述无效）: '//label[contains(., "我已阅读并同意")]//input[@type="checkbox"]'
            print(f"正在勾选同意协议: {agreement_checkbox_selector}")
            try:
                await page.locator(agreement_checkbox_selector).check()
                print("已勾选同意协议")
            except Exception as e:
                print(f"使用选择器 {agreement_checkbox_selector} 勾选复选框失败: {e}")
                # 可以尝试备用选择器或报告错误

            # 点击此页面的下一步按钮
            personal_info_next_button_selector = 'button[data-test="login-phone-next-btn"]' # 根据提供的HTML更新的选择器
            print(f"正在点击个人信息页面的下一步按钮: {personal_info_next_button_selector}")
            await page.locator(personal_info_next_button_selector).click()
            print("已点击个人信息页面的下一步")

            # --- 短信验证码处理 ---
            print("等待验证码输入页面加载...")
            # 假设验证码输入框的选择器，需要根据实际页面调整
            code_input_selector = 'input[placeholder="请输入验证码"]' 
            await page.locator(code_input_selector).wait_for(state='visible', timeout=100000)
            print("验证码输入页面加载完成")

            # 自动化处理短信验证码通常比较困难，因为需要外部交互（接收短信）
            # 此处暂停等待手动输入
            print("请在控制台输入收到的短信验证码：")
            verification_code = input()

            # 定位验证码输入框并输入
            print(f"正在定位验证码输入框: {code_input_selector}")
            await page.locator(code_input_selector).fill(verification_code)
            print("已输入验证码")

            # 点击最终的注册/下一步按钮
            # 注意：选择器需要根据实际页面调整，可能是“注册”、“完成”或“下一步”
            final_register_button_selector = 'button:has-text("注册")' # 示例选择器
            print(f"正在点击最终注册按钮: {final_register_button_selector}")
            await page.locator(final_register_button_selector).click()
            print("已点击最终注册按钮")

            # --- 获取多维表格授权码 --- 
            print("等待注册后页面跳转或加载...")
            await page.wait_for_timeout(5000) # 等待页面稳定

            template_url = "YOUR_TEMPLATE_LINK_HERE" # 请替换为实际的模板链接
            auth_token = await get_template_auth_code(page, template_url)
            print(f"最终获取到的授权码: {auth_token}")
            # TODO: 将 auth_token 保存到本地文件或变量

            # --- 后续步骤 --- 
            # 注册流程（初步）完成，请根据实际页面继续完善后续步骤
            print("注册及授权码获取流程完成")
            # 留出一些时间查看结果
            await page.wait_for_timeout(5000) # 等待5秒

        except Exception as e:
            print(f"发生错误: {e}")
            # 可以增加截图等错误处理逻辑
            await page.screenshot(path="error_screenshot.png")
            print("已保存错误截图: error_screenshot.png")

        finally:
            # 关闭浏览器
            await browser.close()
            print("浏览器已关闭")

async def test_get_auth_code():
    """测试获取模板授权码的功能。"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        try:
            # --- 导航到飞书登录页面并等待手动登录 ---
            print("正在访问飞书登录页面...")
            await page.goto("https://www.feishu.cn/") # 导航到飞书主页或登录页
            await page.wait_for_load_state('networkidle')
            print("页面加载完成")

            print("请在浏览器中手动登录飞书账号。")
            print("登录成功后，请按 Enter 键继续执行后续测试...")
            input() # 等待用户确认登录完成
            print("手动登录确认，继续执行脚本...")

            # --- 调用获取授权码的函数 --- 
            # 登录后，页面应该处于登录状态，可以直接进行后续操作
            print("准备调用 get_template_auth_code 函数...")

            template_url = "https://khhyqkwejc.feishu.cn/wiki/XzmYwsjaVi9B3Oki0ikcHCrknOf?from=from_copylink" # !! 请替换为实际的模板链接 !!
            print("开始测试 get_template_auth_code...")
            auth_token = await get_template_auth_code(page, template_url)

            if auth_token:
                print(f"测试成功！获取到的授权码: {auth_token}")
            else:
                print("测试失败，未能获取到授权码。")

            await page.wait_for_timeout(5000) # 等待查看结果

        except Exception as e:
            print(f"测试过程中发生错误: {e}")
            await page.screenshot(path="test_error_screenshot.png")
            print("已保存测试错误截图: test_error_screenshot.png")

        finally:
            await browser.close()
            print("测试浏览器已关闭")

if __name__ == "__main__":
    # 运行注册流程
    # asyncio.run(register_feishu("YOUR_PHONE_NUMBER")) # 替换为你的手机号

    # 或者运行测试流程
    print("开始运行授权码获取测试...")
    # !! 重要: 运行测试前请确保 YOUR_TEMPLATE_LINK_HERE 已替换 !!
    # !! 同时确保测试手机号 test_phone_number 是有效的 !!
    asyncio.run(test_get_auth_code())