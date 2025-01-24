var dagfuncs = (window.dashAgGridFunctions = window.dashAgGridFunctions || {});

// allows tooltip to expand outside the grid
dagfuncs.setPopupsParent = () => {
    return document.querySelector('body')
}