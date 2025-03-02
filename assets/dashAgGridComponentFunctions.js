var dagcomponentfuncs = (window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {});

//format particular countries to match icon name
const particularCountries = {
    'brunei-darussalam': 'brunei',
    'cabo-verde': 'cape-verde',
    'congo': 'congo-brazzaville',
    "cote-d'ivoire": 'cote-divoire',
    "democratic-people's-republic-of-korea": 'north-korea',
    'democratic-republic-of-the-congo': 'congo-kinshasa',
    "lao-people's-democratic-republic": 'laos',
    'myanmar': 'myanmar-burma',
    'republic-of-korea': 'south-korea',
    'saint-kitts-and-nevis': 'st-kitts-and-nevis',
    'saint-lucia': 'st-lucia',
    'saint-vincent-and-the-grenadines': 'st-vincent-and-grenadines',
    'state-of-palestine': 'palestinian-territories',
    'syrian-arab-republic': 'syria',
    'viet-nam': 'vietnam'
}

dagcomponentfuncs.CountriesCell = function (props) {
    if (!props.value) {
        return '-'
    }

    let countries = props.value.split(", ")
    let cellChildren = []

    for (const country of countries) {
        // main formatting
        let formattedCountry = country.toLowerCase().replace(/\(.*\)/, '').trim().replaceAll(" ", '-')
        // format particular countries
        if (formattedCountry in particularCountries) {
            formattedCountry = formattedCountry.replace(formattedCountry, particularCountries[formattedCountry])
        }

        // add the flag icon and country name
        cellChildren.push(
            React.createElement(
                window.dash_iconify.DashIconify,
                {
                    icon: `twemoji:flag-${formattedCountry}`,
                    width: 30,
                    style: {minWidth: 30}
                },
            ),
            React.createElement(
                "span",
                {style: {marginLeft: 5, marginRight: 10}},
                country
            )
        )
    }
    return React.createElement(
        "div",
        {style: {display: 'flex', 'alignItems': 'center', padding: '0px 5px'}},
        cellChildren
    )
}

dagcomponentfuncs.CustomTooltipCountries = function (props) {
    if (!props.value) {
        return '-'
    }

    let countries = props.value.split(", ")
    let tooltipChildren = []

    for (const country of countries) {
        // main formatting
        let formattedCountry = country.toLowerCase().replace(/\(.*\)/, '').trim().replaceAll(" ", '-')
        // format particular countries
        if (formattedCountry in particularCountries) {
            formattedCountry = formattedCountry.replace(formattedCountry, particularCountries[formattedCountry])
        }

        // add the flag icon and country name
        tooltipChildren.push(
            React.createElement(
                "div",
                {style: {display: 'flex', alignItems: 'center', gap: 5}},
                [
                    React.createElement(
                        window.dash_iconify.DashIconify,
                        {icon: `twemoji:flag-${formattedCountry}`, width: 30, style: {minWidth: 30}},
                    ),
                    country
                ]
            )
        )
    }
    return React.createElement(
        "div",
        {
            className: "ag-tooltip ag-tooltip-interactive ag-popup-child",
            style: {display: 'flex', flexDirection: 'column', width: 200}
        },
        tooltipChildren
    )
}

dagcomponentfuncs.CheckBool = function (props) {
    // no bool styling for bottom pinned row
    if (props.node.rowPinned === 'bottom') {
        return props.value
    }
    if (props.value) {
        primaryColor = window.getComputedStyle(document.body).getPropertyValue('--primary')
        return React.createElement(
            window.dash_iconify.DashIconify,
            {icon: 'mingcute:check-fill', width: 25, color: primaryColor},
        );
    } else {
        return '-'
    }
}


dagcomponentfuncs.CustomTooltipHeaders = function (props) {
    return React.createElement(
        window.dash_core_components.Markdown,
        {
            style: {
                textWrap: 'nowrap',
                // boxShadow: `0 1px 4px 1px ${boxShadowColor}`
                // 'border-color': 'var(--bs-primary)'

            },
            dangerously_allow_html: true,
            link_target: '_blank',
            className: "ag-tooltip ag-tooltip-interactive ag-popup-child"
        },
        props.value
    )
}

dagcomponentfuncs.InternalLinkCell = function (props) {
    const {setData, data} = props;

    const country_or_entity = data['Country Name' in data ? 'Country Name' : 'Entity']
    const tooltipText = country_or_entity === 'TOTAL' ?
        `All filtered ${'Country Name' in data ? "Countries" : "Entities"}` : country_or_entity

    const tooltipLabel = React.createElement(window.dash_core_components.Markdown, {},
        `Go to **${tooltipText}** 
        ${props.column.colId === '# RP' ? 'Readiness Programmes' : 'Funded Activities'} Dashboard`,
    )

    const tooltipBackground = window.getComputedStyle(document.body).getPropertyValue('--mantine-color-body')
    const tooltipTextColor = window.getComputedStyle(document.body).getPropertyValue('--mantine-color-text')

    function onClick() {
        setData(country_or_entity);
    }

    return React.createElement(
        "div",
        {style: {display: 'flex', 'alignItems': 'center', width: '100%', padding: '0px 5px'}},
        [
            React.createElement(
                "div",
                {style: {flex: 1, textAlign: 'center'}},
                props.value,
            ),
            React.createElement(
                window.dash_mantine_components.Tooltip,
                {label: tooltipLabel, display: 'flex', position: "left", bg: tooltipBackground, c: tooltipTextColor},
                React.createElement(
                    window.dash_mantine_components.Center, {},
                    React.createElement(
                        window.dash_iconify.DashIconify,
                        {
                            onClick,
                            icon: 'iconamoon:arrow-top-right-1-light', height: 25,
                            className: "custom-cell-icon-link", //custom class adding hover effect
                        },
                    ),
                ),
            ),
        ]
    )
}

dagcomponentfuncs.ExternalLinkCell = function (props) {

    const tooltipBackground = window.getComputedStyle(document.body).getPropertyValue('--mantine-color-body')
    const tooltipTextColor = window.getComputedStyle(document.body).getPropertyValue('--mantine-color-text')

    return React.createElement(
        "div",
        {style: {display: 'flex', 'alignItems': 'center', width: '100%', gap: '10px'}},
        [
            React.createElement(
                window.dash_mantine_components.Tooltip,
                {
                    label: 'Visit the GCF Webpage of the Project for More Details.',
                    display: 'flex', position: "right", bg: tooltipBackground, c: tooltipTextColor
                },
                React.createElement(
                    'a', {href: 'https://www.greenclimate.fund/project/' + props.data['Ref #'], target: '_blank'},
                    React.createElement(
                        window.dash_mantine_components.Center, {},
                        React.createElement(
                            window.dash_iconify.DashIconify, {icon: 'mingcute:external-link-line', height: 25}
                        ),
                    )
                ),
            ),
            React.createElement("div", {}, props.value),
        ]
    )
}


dagcomponentfuncs.CustomReadinessStatusCell = function (props) {

    let width = props.value === "In Legal Processing" ? 120 : null
    let color = {
        'Cancelled': '#d43a2f',
        'In Legal Processing': '#f0ad4e',
        'Legal Agreement Effective': '#ffdd33',
        'Disbursed': '#97cd3f',
        'Closed': '#15a14a'
    }
    let icon = {
        "Cancelled": "mdi:cancel",
        "In Legal Processing": "ic:round-gavel",
        "Legal Agreement Effective": "ic:outline-handshake",
        "Disbursed": "ic:baseline-attach-money",
        "Closed": "ic:outline-check-circle"
    }
    let iconWidth = ["In Legal Processing", "Legal Agreement Effective"].includes(props.value) ? 25 : 15

    return React.createElement(
        window.dash_mantine_components.Badge,
        {style: {width: width, maxWidth: 150, height: 30}, color: color[props.value], variant: 'outline'},
        React.createElement(
            "div",
            {style: {display: 'flex', alignItems: 'center', gap: 5}},
            [
                React.createElement(window.dash_iconify.DashIconify, {icon: icon[props.value], width: iconWidth}),
                React.createElement("span", {style: {textWrap: 'wrap', lineHeight: 1.1}}, props.value)
            ]
        )
    )
}
