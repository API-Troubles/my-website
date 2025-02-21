// Global variables (All null until dom loads to set them)
//    Charts:
// ignore (?<!\/)\/(?!\/)(?!\/\*)(?!\*\/)
let cpuGraph = null;
let memoryGraph = null;
let storageGraph = null;

//    The Stat Texts:
let table = null;

let cpuStats = null;
let memoryStats = null;
let storageStats = null;

//    Store graph data to use easily
let cpuDataset = {
    global: {
        globalUsage: Array(30).fill(null),
        myUsage: Array(30).fill(null)
    },
    perCore: Array(30).fill(null), // This will contain further arrays for each core
    cores: 0,
    dataSource: "global-usage",
    changeSource: false
};

let memoryDataset = {
    global: {
        globalUsage: Array(30).fill(null)
    },
    max: 0,
    dataSource: "global-usage",
    changeSource: false
};
// end global variables


function getOptionData(limit, addScale, scaleMax = 100, unit = "%") {
    let options = {
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    usePointStyle: true,
                    pointStyle: 'circle',
                    boxHeight: 8
                }
            },
            tooltip: {
                enabled: false, // Disable tooltips
                callbacks: {
                    label: function(context) {
                        let label = context.dataset.label || '';

                        if (context.parsed !== null) {
                            label += `: ${context.parsed} ${unit}`;
                        }

                        return label;
                    }
                }
            }
        },
        animation: false,
        elements: {
            point: {
                radius: 0 // default to disabled in all datasets
            }
        },
        maintainAspectRatio: false
    }
    if (addScale) {
        options.scales = {
            y: {
                min: 0,
                max: scaleMax,
                ticks: {
                    callback: function(value) {
                        return value + unit;
                    }
                }
            }
        }
    }
    if (limit !== null) {
        options.plugins.annotation = {
            annotations: [{
                type: 'line',
                mode: 'horizontal',
                scaleID: 'y-axis-0',
                yMin: limit,
                yMax: limit,
                borderColor: 'red',
                borderWidth: 2,
                label: {
                    content: 'Threshold'
                }
            }]
        }
    }
    return options
}

function updateGraphs() {
    fetch("/data")
    .then((response) => {
        if (response.status === 200) {
            return response.json()
        } else {
            console.warn(`Couldn't fetch global data - HTTP ${response.status}`)
            return null
        }
    })
    .then((data) => {
        const table = document.getElementById("pid-chart");
        const warningPrompt = document.getElementById("warning-prompt");

        let myCpuUsage = 0;
        let myMemUsage = 0;

        // Clear rows on table before adding data

        // CREDIT: Thanks stackoverflow
        // https://stackoverflow.com/questions/16270087/delete-all-rows-on-a-table-except-first-with-javascript
        var rows = table.rows;
        var i = rows.length;
        while (--i) {
            table.deleteRow(i);
        }

        if (data === null) { // Print nothing when data missing for whatever reason
            // Show warning if its not displayed already
            if (warningPrompt.style.display === "none") {
                warningPrompt.style.display = "block";
            }

            pushShift(cpuDataset.global.globalUsage, null);
            pushShift(cpuDataset.global.myUsage, null);
            pushShift(cpuDataset.perCore, null);

            cpuGraph.data.datasets.forEach((dataset) => {
                pushShift(dataset.data, null);
            });
            memoryGraph.data.datasets.forEach((dataset) => {
                pushShift(dataset.data, null);
            });

            console.log("updated graphs without adding data");
            cpuGraph.update();
            memoryGraph.update();
            return
        }
        // Hide warning prompt if it was displayed
        if (warningPrompt.style.display === "block") {
            warningPrompt.style.display = "none";
        }
        // My CPU and memory data + add data to table
        // These all use the same forEach loop so may as well combine
        data.by_pid.forEach((process) => {
            myCpuUsage += process.cpu;
            myMemUsage += process.memory;

            // Credit: ChatGPT helped to make code more concise
            const newRow = table.insertRow(table.rows.length);
            const rowData = [
                process.pid,
                process.name,
                process.cpu,
                convert(process.memory, "GB", 2),
                process.status
            ];

            rowData.forEach((value, index) => {
                newRow.insertCell(index).textContent = value;
            });
        });

        // Add global data
        pushShift(cpuDataset.global.globalUsage, data.total.cpu.usage);
        pushShift(cpuDataset.global.myUsage, roundDecimal(myCpuUsage, 2));
        // Add core usage + core count
        pushShift(cpuDataset.perCore, data.total.cpu["per-core"]);
        if (cpuDataset.cores === 0) {
            cpuDataset.cores = parseInt(data.total.cpu["per-core"].length);
        }

        // Add data to chart depending on chart type
        if (cpuDataset.dataSource === "global-usage") {
            cpuGraph.data.datasets[0].data = cpuDataset.global.myUsage;
            cpuGraph.data.datasets[1].data = cpuDataset.global.globalUsage;

            // Debugging stuff, TODO Trace weird bug
            /*
            if (parseFloat(cpuDataset.global.myUsage.slice(-1)) >= parseFloat(cpuDataset.global.globalUsage.slice(-1))) {
                    console.warn(`How on earch is my usage higher than global? Global is ${cpuDataset.global.globalUsage.slice(-1)}, mine is ${cpuDataset.global.myUsage.slice(-1)}`);
            } */

        } else if (cpuDataset.dataSource === "core-usage") {
            cpuDataset.perCore.forEach((history) => {
                let i = 0;
                if (history === null) {
                    cpuGraph.data.datasets.forEach((dataset) => {
                        pushShift(dataset.data, null); // TODO: Change that
                    });
                    return
                }
                // So all the core frequencies for that time period, in order
                history.forEach((coreFreq) => {
                    pushShift(cpuGraph.data.datasets[i].data, coreFreq);
                    i++;
                })
            })
        }

        updateCpuTxt(data)

        // Save memory data
        pushShift(memoryDataset.global.globalUsage, convert(data.total.memory.used, "GB", 2));

        // Memory Data
        pushShift(memoryGraph.data.datasets[0].data, convert(myMemUsage, "GB", 2));
        if (memoryDataset.dataSource === "global-usage") { 
            memoryGraph.data.datasets[1].data = memoryDataset.global.globalUsage;
        }

        updateMemoryTxt(data);

        // Display a table total
        let totalRow = table.insertRow(table.rows.length);
        totalRow.insertCell(0).textContent = 'TOTAL:';
        totalRow.insertCell(1).textContent = '';
        totalRow.insertCell(2).textContent = roundDecimal(myCpuUsage, 2);
        totalRow.insertCell(3).textContent = convert(myMemUsage, "GB", 2),
        totalRow.insertCell(4).textContent = '';

        // Updates graphs at the end
        console.log("updated graphs");
        cpuGraph.update();
        memoryGraph.update();
    });
}

function roundDecimal(number, roundTo) {
    return parseFloat((number).toFixed(roundTo))
}

function convert(byte_value, unit, round) {
    if (typeof round !== "number" && round !== undefined) {
        throw new Error(`${round} is not a valid number to round to!`)
    }
    unit = unit.toUpperCase()
    result = null;
    if (unit === "KB") {
        result = byte_value / (2**10)
    } else if (unit === "MB") {
        result = byte_value / (2**20)
    } else if (unit === "GB") {
        result = byte_value / (2 ** 30)
    } else if (unit === "TB") {
        result = byte_value / (2 ** 40)
    } else {
        throw new Error(`${unit} is not a valid unit!`);
    }
    if (round) {
        return roundDecimal(result, round)
    } else {
        return result
    }
}

function pushShift(array, item) {
    // A quick function to push and shift an array to maintain the chart size
    array.push(item);
    array.shift();
}

function updateCpuTxt(data) {
    let myCpuUsage = 0;

    data.by_pid.forEach((process) => {
        myCpuUsage += process.cpu;
    });

    if (cpuDataset.dataSource === "global-usage") {
        cpuStats.textContent = `Global Usage: ${data.total.cpu.usage}%`;
    } else if (cpuDataset.dataSource === "core-usage") {
        cpuStats.textContent = roundDecimal(myCpuUsage, 2) + "%";
    }
}

function updateMemoryTxt(data) {
    if (cpuDataset.dataSource === "global-usage") {
        if (memoryStats.matches(':hover')) {
            memoryStats.textContent = `${convert(data.total.memory.used, "GB", 2)} GB / ${convert(data.total.memory.total, "GB", 2)} GB`;
        } else {
            memoryStats.textContent = data.total.memory.percent + "%";
        }
    } else if (cpuDataset.dataSource === "my-usage") {
        // TODO
        console.log("uhhh")
    }
}

function updateStorageTxt(data) {
    if (storageStats.matches(':hover')) {
        storageStats.textContent = `${convert(data.total.storage.used, "GB", 2)} GB / ${convert(data.total.storage.total, "GB", 2)} GB`
    } else {
        storageStats.textContent = data.total.storage.percent + "%";
    }
}

// Thanks to
// https://www.w3schools.com/howto/howto_css_button_group.asp
// and ChatGPT for help on some of the js
function selectButton(button, group) {
    const buttons = document.querySelectorAll(`.graph-selector[data-group="${group}"] .toggle-button`); // Get all toggle-btn classes in a group in a graph-selector class
    if (button.classList.contains('selected')) {
        return // Don't do anything if pressed btn alr selected
    }
    buttons.forEach(btn => {
        btn.classList.remove('selected'); 
    });
    button.classList.add('selected');

    if (group == "cpu-options") {
        cpuDataset.dataSource = button.name;
        if (button.name === "global-usage") {
            cpuGraph.data.datasets = [{
                label: 'My Usage',
                data: Array(30).fill(null),
                fill: true,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)'
            }, {
                label: 'Global Usage',
                data: Array(30).fill(null),
                fill: true,
                backgroundColor: 'rgba(201, 203, 207, 0.2)',
                borderColor: 'rgba(201, 203, 207, 1)'
            }]
        } else if (button.name === "core-usage") {
            cpuGraph.data.datasets = [];
            for (let i = 1; i <= cpuDataset.cores; i++) {
                cpuGraph.data.datasets.push({
                    label: `Core #${i}`,
                    data: Array(30).fill(null),
                    fill: true,
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)'
                });
            }
        }
        cpuGraph.update();
        
    } else if (group == "memory-options") {
        memoryDataset.dataSource = button.name;
        if (button.name === "global-usage") {
            memoryGraph.data.datasets.push({
                label: 'Global Usage',
                data: Array(30).fill(null),
                fill: true,
                backgroundColor: 'rgba(201, 203, 207, 0.2)',
                borderColor: 'rgba(201, 203, 207, 1)'
            })
            memoryGraph.options.scales.y.max = memoryDataset.max;
        } else if (button.name === "my-usage") {
            memoryGraph.data.datasets.pop() // Remove global value
            memoryDataset.max = memoryGraph.options.scales.y.max;
            memoryGraph.options.scales.y.max = 2;
        }
        memoryGraph.update();

    } else if (group == "storage-options") {
        fetch("/data")
        .then((response) => response.json())
        .then((data) => {
            let chart_labels = [];
            let chart_data = [];
            data.by_dir.forEach((directory) => {
                if (directory[1] == "." || directory[1] == "/home/runner/Nest-Website") { // Ignore the root filepaths
                    return
                }
                else if (directory[1] == "total") { // Get total storage usage
                    myStorageUsage = directory[0]
                    return
                }

                chart_labels.push(directory[1]);
                chart_data.push(convert(directory[0], "GB", 5)); // Numbers small
            });

            if (button.name == "global-usage") {
                storageGraph.data.labels = ["My Usage", "Storage Left", "Other Usage"];
                storageGraph.data.datasets[0].data = [
                    convert(myStorageUsage, "GB", 3),
                    convert(data.total.storage.free, "GB", 3),
                    convert(data.total.storage.used - myStorageUsage, "GB", 3)
                ];
                storageGraph.data.datasets[0].backgroundColor = [
                    'rgb(54, 162, 235)', 
                    'rgb(211,211,211)', 
                    'rgb(255, 99, 132)'
                ]

            } else if (button.name == "my-usage") {
                console.log(storageGraph.data)
                storageGraph.data.datasets[0].backgroundColor = [
                    'rgb(255, 99, 132)', 'rgb(54, 162, 235)', 'rgb(255, 203, 92)', 'rgb(255, 163, 26)', 'rgb(92, 185, 94)', 'rgb(165, 56, 182)']
                chart_labels.push("Space Left");
                chart_data.push(2 - convert(myStorageUsage, "GB"));
                storageGraph.data.labels = chart_labels;
                storageGraph.data.datasets[0].data = chart_data;

            } else if (button.name == "directory-usage") {
                storageGraph.data.labels = chart_labels;
                storageGraph.data.datasets[0].data = chart_data;
                storageGraph.data.datasets[0].backgroundColor = [
                    'rgb(255, 99, 132)', 'rgb(54, 162, 235)', 'rgb(255, 203, 92)', 'rgb(255, 163, 26)', 'rgb(92, 185, 94)', 'rgb(165, 56, 182)']
            }

            storageGraph.update();
        });
    }
}

const cpuData = {
    labels: Array(30).fill(""),
    datasets: [{
        label: 'My Usage',
        data: Array(30).fill(null),
        fill: true,
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        borderColor: 'rgba(54, 162, 235, 1)'
    }, {
        label: 'Global Usage',
        data: Array(30).fill(null),
        fill: true,
        backgroundColor: 'rgba(201, 203, 207, 0.2)',
        borderColor: 'rgba(201, 203, 207, 1)'
    }]
}

const memoryData = {
    labels: Array(30).fill(""),
    datasets: [{
        label: 'My Usage',
        data: Array(30).fill(null),
        fill: true,
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        borderColor: 'rgba(54, 162, 235, 1)'
    }, {
        label: 'Global Usage',
        data: Array(30).fill(null),
        fill: true,
        backgroundColor: 'rgba(201, 203, 207, 0.2)',
        borderColor: 'rgba(201, 203, 207, 1)'
    }]
}

const storageData = {
    labels: [],
    datasets: [{
        label: "Storage",
        data: [],
        fill: true,
        backgroundColor: [
            'rgb(54, 162, 235)', 
            'rgb(211,211,211)', 
            'rgb(255, 99, 132)'
        ],
        hoverOffset: 15,
        borderColor: 'rgba(54, 162, 235, 1)'
    }]
}


document.addEventListener("DOMContentLoaded", (event) => {
    console.log("DOM has fully loaded");

    // Set global variables on DOM loading
    chart = document.getElementById("pid-chart");
    cpuStats = document.getElementById("cpu-usage");
    memoryStats = document.getElementById("memory-usage");
    storageStats = document.getElementById("storage-usage");

    // Get data
    fetch("/data")
    .then((response) => response.json())
    .then((data) => {
        console.log("Loaded global data");

        updateCpuTxt(data);
        updateMemoryTxt(data);
        updateStorageTxt(data);

        cpuGraph = new Chart("cpu-graph", {
            type: 'line',
            data: cpuData,
            options: getOptionData(null, true)
        });

        cpuStats.addEventListener("mouseover", (event) => updateCpuTxt(data));
        cpuStats.addEventListener("mouseout", (event) => updateCpuTxt(data));

        // We need global data to set this graph
        memoryGraph = new Chart("memory-graph", {
            type: 'line',
            data: memoryData,
            options: getOptionData(2, true, convert(data.total.memory.total, "GB", 2), " GB")
        });

        memoryStats.addEventListener("mouseover", (event) => updateMemoryTxt(data));
        memoryStats.addEventListener("mouseout", (event) => updateMemoryTxt(data));

        let storageOptions = getOptionData(null, false, null, "GB");
        storageOptions.animation = true;
        storageOptions.plugins.tooltip.enabled = true;

        storageGraph = new Chart("storage-graph", {
            type: 'doughnut',
            data: storageData,
            options: storageOptions
        });

        storageStats.addEventListener("mouseover", (event) => updateStorageTxt(data));
        storageStats.addEventListener("mouseout", (event) => updateStorageTxt(data));


        let myStorageUsage = null;
        data.by_dir.forEach((directory) => {
            // Add storage data :D
            if (directory[1] == ".") { // Ignore the root filepath
                return
            }
            if (directory[1] == "total") { // Get total storage usage
                myStorageUsage = directory[0];
            }
        });

        storageGraph.data.labels = ["My Usage", "Storage Left", "Other Usage"];
        storageGraph.data.datasets[0].data = [myStorageUsage / (1024 ** 3), data.total.storage.free / (1024 ** 3), (data.total.storage.used - myStorageUsage) / (1024 ** 3)];
        storageGraph.data.datasets[0].backgroundColour = ['rgb(54, 162, 235)', 'rgb(211,211,211)', 'rgb(255, 99, 132)']

        storageGraph.update();

        // Make charts update every second, on the second
        // CREDIT: thx chatgpt for the help
        const now = new Date();
        const delay = 1000 - (now.getMilliseconds());

        setTimeout(() => {
            updateGraphs();
            setInterval(updateGraphs, 1000);
        }, delay);
    });
});