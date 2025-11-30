const navItems = [
    { key: 'dashboard', label: 'ダッシュボード', href: 'index.html', icon: 'layout-dashboard' },
    { key: 'employees', label: '従業員', href: 'employees.html', icon: 'users' },
    { key: 'companies', label: '派遣先', href: 'haken-saki.html', icon: 'factory' },
    { key: 'imports', label: 'インポート', href: 'import.html', icon: 'upload-cloud' },
    { key: 'ocr', label: 'OCRスキャナー', href: 'ocr-scanner.html', icon: 'scan' },
    { key: 'renewal', label: '更新申請', href: 'visa-renewal.html', icon: 'refresh-ccw' },
    { key: 'coe', label: '認定申請', href: 'visa-coe.html', icon: 'file-badge' },
    { key: 'reports', label: 'レポート', href: 'reports.html', icon: 'bar-chart-3' },
];

function renderAppShell({ active = 'dashboard', headline = 'UNS Visa Management System', subtitle = '派遣会社向けビザ管理プラットフォーム' } = {}) {
    const shell = document.createElement('div');
    shell.className = 'app-shell';
    shell.innerHTML = `
        <div class="nav-inner">
            <div class="flex items-center justify-between">
                <div class="app-brand">
                    <span class="brand-badge">🇯🇵</span>
                    <div>
                        <div class="brand-text">UNS Visa</div>
                        <div class="text-sm text-slate-300">${headline}</div>
                    </div>
                </div>
                <div class="nav-meta">
                    <span class="pill flex items-center gap-2"><i data-lucide="shield-check"></i> 安全な社内利用</span>
                    <span class="pill flex items-center gap-2"><i data-lucide="clock-3"></i> 24時間稼働</span>
                </div>
            </div>
            <div class="nav-meta mt-3">
                <div class="flex items-center gap-2 text-slate-300">
                    <span class="text-white font-semibold">${headline}</span>
                    <span class="text-slate-400">/</span>
                    <span>${subtitle}</span>
                </div>
                <a href="login.html" class="text-sm text-blue-300 hover:text-white transition-colors flex items-center gap-2">
                    <i data-lucide="log-in"></i><span>ログイン</span>
                </a>
            </div>
            <div class="nav-links">
                ${navItems.map(item => `
                    <a class="nav-link ${item.key === active ? 'active' : ''}" href="${item.href}" aria-label="${item.label}">
                        <i data-lucide="${item.icon}" class="nav-icon"></i>
                        <span>${item.label}</span>
                    </a>
                `).join('')}
            </div>
        </div>
    `;

    document.body.insertAdjacentElement('afterbegin', shell);

    if (window.lucide && typeof window.lucide.createIcons === 'function') {
        window.lucide.createIcons();
    }
}

function renderFooter() {
    const footer = document.createElement('footer');
    footer.className = 'footer text-sm';
    footer.innerHTML = `
        <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-2 text-slate-400">
            <div class="flex items-center gap-2 justify-center">
                <i data-lucide="sparkles" class="w-4 h-4"></i>
                <span>UNS Visa Management System v1.0</span>
            </div>
            <div class="flex items-center gap-2 justify-center">
                <i data-lucide="globe-2" class="w-4 h-4"></i>
                <span>© 2024 UNS株式会社 - UI refreshed</span>
            </div>
        </div>
    `;
    document.body.insertAdjacentElement('beforeend', footer);
    if (window.lucide && typeof window.lucide.createIcons === 'function') {
        window.lucide.createIcons();
    }
}

window.renderAppShell = renderAppShell;
window.renderFooter = renderFooter;
