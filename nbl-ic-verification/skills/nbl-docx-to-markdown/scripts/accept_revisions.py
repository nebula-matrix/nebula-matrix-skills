#!/usr/bin/env python3
"""
接受 DOCX 文件中的所有审阅修订(track changes)
用法: python3 accept_revisions.py <input.docx> [output.docx]
"""
import sys
import os
import subprocess
import time

# 确保 python3-uno 可用
sys.path.insert(0, '/usr/lib/python3/dist-packages')
import uno
from com.sun.star.beans import PropertyValue

SOFFICE_PORT = 2002
STARTUP_WAIT = 3  # soffice 启动等待秒数


def start_soffice():
    """在后台启动 LibreOffice 监听服务"""
    cmd = [
        'soffice',
        '--headless',
        '--invisible',
        '--norestore',
        '--nologo',
        '--nolockcheck',
        '--nodefault',
        f'--accept=socket,host=localhost,port={SOFFICE_PORT};urp;StarOffice.ComponentContext'
    ]
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(STARTUP_WAIT)
    return proc


def connect_soffice():
    """通过 UNO 连接到 soffice"""
    local_ctx = uno.getComponentContext()
    resolver = local_ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", local_ctx)

    ctx = resolver.resolve(
        f"uno:socket,host=localhost,port={SOFFICE_PORT};urp;StarOffice.ComponentContext")
    smgr = ctx.ServiceManager
    desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
    return desktop, smgr, ctx


def get_filter_name(ext):
    """根据文件扩展名获取 LibreOffice 过滤器名称"""
    mapping = {
        '.docx': 'Office Open XML Text',
        '.doc': 'MS Word 97',
        '.odt': 'ODF Text Document',
        '.rtf': 'Rich Text Format',
        '.html': 'HTML:UTF8',
    }
    return mapping.get(ext.lower(), '')


def accept_all_revisions(input_file, output_file=None):
    input_path = os.path.abspath(input_file)

    if output_file is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_accepted{ext}"
    else:
        output_path = os.path.abspath(output_file)

    # 启动 soffice
    print(f"[*] 启动 LibreOffice 监听服务 (端口 {SOFFICE_PORT})...")
    proc = start_soffice()

    try:
        print("[*] 连接 UNO 接口...")
        desktop, smgr, ctx = connect_soffice()

        # 打开文档 (Hidden 模式)
        print(f"[*] 打开文档: {input_path}")
        file_url = uno.systemPathToFileUrl(input_path)
        load_props = (PropertyValue("Hidden", 0, True, 0),)
        doc = desktop.loadComponentFromURL(file_url, "_blank", 0, load_props)

        if doc is None:
            raise RuntimeError("无法打开文档")

        # 接受所有修订
        print("[*] 接受所有修订...")
        try:
            frame = doc.getCurrentController().getFrame()
            dispatch = smgr.createInstanceWithContext(
                "com.sun.star.frame.DispatchHelper", ctx)
            dispatch.executeDispatch(
                frame, ".uno:AcceptAllTrackedChanges", "", 0, ())
            print("    ✓ 已完成")
        except Exception as e:
            print(f"    ! dispatch 命令失败: {e}")
            # 备用方案：尝试通过 Redlines API
            try:
                redlines = doc.getRedlines()
                redlines.acceptAll()
                print("    ✓ 已通过 Redlines API 完成")
            except Exception as e2:
                print(f"    ! Redlines API 也失败: {e2}")
                raise

        # 保存
        print(f"[*] 保存到: {output_path}")
        out_url = uno.systemPathToFileUrl(output_path)

        ext = os.path.splitext(output_path)[1].lower()
        filter_name = get_filter_name(ext)

        if filter_name:
            save_props = (
                PropertyValue("Overwrite", 0, True, 0),
                PropertyValue("FilterName", 0, filter_name, 0),
            )
        else:
            save_props = (PropertyValue("Overwrite", 0, True, 0),)

        doc.storeAsURL(out_url, save_props)
        doc.close(True)
        print("    ✓ 已保存")

    finally:
        # 终止 soffice
        print("[*] 关闭 LibreOffice...")
        try:
            desktop.terminate()
        except:
            pass
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        print("    ✓ 已关闭")

    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 accept_revisions.py <input.docx> [output.docx]")
        sys.exit(1)

    out = accept_all_revisions(
        sys.argv[1],
        sys.argv[2] if len(sys.argv) > 2 else None
    )
    print(f"\n[OK] 输出文件: {out}")
