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
        {
            style: {display: 'flex', 'alignItems': 'center', padding: '0px 5px'}
        },
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

dagcomponentfuncs.CustomButtonCell = function (props) {
    // // no icon for bottom pinned row
    // if (props.node.rowPinned == 'bottom') {
    //     return props.value
    // }

    const {setData, data} = props;

    function onClick() {
        console.log(data)
        setData(data['Country Name']);
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
                window.dash_iconify.DashIconify,
                {
                    onClick,
                    icon: 'mingcute:external-link-line',
                    className: "custom-cell-icon-link", //custom class adding hover effect
                    width: 20,
                },
            )
        ]
    )
}

// dagcomponentfuncs.CustomButtonCell = function (props) {
//     const {setData, data} = props;
//
//     function onClick() {
//         setData();
//     }
//
//     return React.createElement(
//         window.dash_bootstrap_components.ActionIcon,
//         {
//             onClick,
//             color: props.color,
//         },
//         [
//             props.value,
//             React.createElement(
//                 window.dash_iconify.DashIconify,
//                 {icon: 'mingcute:check-fill', width: 25, color: primaryColor},
//             )
//         ]
//     );
// if (props.value) {
//     primaryColor = window.getComputedStyle(document.body).getPropertyValue('--primary')
//     return React.createElement(
//         window.dash_iconify.DashIconify,
//         {icon: 'mingcute:check-fill', width: 25, color: primaryColor},
//     );
// } else {
//     return '-'
// }
// }

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
