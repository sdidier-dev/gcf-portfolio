var dagfuncs = (window.dashAgGridFunctions = window.dashAgGridFunctions || {});

// allows tooltip to expand outside the grid
dagfuncs.setPopupsParent = () => {
    return document.querySelector('body')
}


// custom function to have $1B instead of $1G, as it is not possible with D3-formatting, used for dag similar to
// the python function in app_config.py
dagfuncs.formatMoneyNumberSI = (number) => {
    const units = ['', 'k', 'M', 'B'];
    let magnitude = 0;
    while (Math.abs(number) >= 1000 && magnitude < units.length - 1) {
        number /= 1000.0;
        magnitude += 1;
    }
    return `$${number.toFixed(2)}${units[magnitude]}`;
}