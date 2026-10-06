// =====================================================
// SMART CANTEEN MANAGEMENT & ANALYTICS DASHBOARD
// =====================================================


// =====================================================
// 1. SUMMARY CARDS
// =====================================================

document.getElementById("totalOrders").textContent =
    totalOrders;

document.getElementById("totalRevenue").textContent =
    "₹" + totalRevenue.toLocaleString("en-IN");

document.getElementById("pendingOrders").textContent =
    pendingOrders;

document.getElementById("unavailableFoodItems").textContent =
    unavailableFoodItems;


// =====================================================
// 2. ORDERS BY FOOD ITEM
// Horizontal + sorted from highest to lowest
// =====================================================

// Combine food names and order counts

const foodData = foodItems.map((name, index) => ({
    name: name,
    orders: foodOrders[index]
}));


// Sort highest → lowest

foodData.sort((a, b) => b.orders - a.orders);


// Separate names and values

const sortedFoodNames =
    foodData.map(item => item.name);

const sortedFoodOrders =
    foodData.map(item => item.orders);


// Create chart

const foodChart =
    document.getElementById("foodChart");


new Chart(foodChart, {

    type: "bar",

    data: {

        labels: sortedFoodNames,

        datasets: [{

            label: "Orders",

            data: sortedFoodOrders

        }]

    },

    options: {

        indexAxis: "y",

        responsive: true,

        maintainAspectRatio: false,

        plugins: {

            legend: {
                display: false
            },

            tooltip: {

                callbacks: {

                    label: function(context) {

                        return " " +
                            context.parsed.x +
                            " orders";

                    }

                }

            }

        },

        scales: {

            x: {

                beginAtZero: true,

                ticks: {
                    stepSize: 2
                },

                title: {

                    display: true,

                    text: "Number of Orders"

                }

            },

            y: {

                ticks: {

                    autoSkip: false,

                    font: {
                        size: 11
                    }

                }

            }

        }

    }

});


// =====================================================
// 3. ORDERS BY TIME
// Bar chart because there are only 2 time buckets
// =====================================================

const timeChart =
    document.getElementById("timeChart");


new Chart(timeChart, {

    type: "bar",

    data: {

        labels: orderTimes,

        datasets: [{

            label: "Orders",

            data: ordersByTime

        }]

    },

    options: {

        responsive: true,

        maintainAspectRatio: false,

        plugins: {

            legend: {
                display: false
            },

            tooltip: {

                callbacks: {

                    label: function(context) {

                        return " " +
                            context.parsed.y +
                            " orders";

                    }

                }

            }

        },

        scales: {

            x: {

                title: {

                    display: true,

                    text: "Order Time"

                }

            },

            y: {

                beginAtZero: true,

                ticks: {

                    stepSize: 10

                },

                title: {

                    display: true,

                    text: "Number of Orders"

                }

            }

        }

    }

});


// =====================================================
// 4. FOOD POPULARITY
// TOP 8 ONLY
// =====================================================


// Create sorted food data

const popularityData =
    foodItems.map((name, index) => ({

        name: name,

        orders: foodOrders[index]

    }));


// Sort highest → lowest

popularityData.sort(
    (a, b) => b.orders - a.orders
);


// Take top 8

const topFoodData =
    popularityData.slice(0, 8);


// Names

const topFoodNames =
    topFoodData.map(item => item.name);


// Orders

const topFoodOrders =
    topFoodData.map(item => item.orders);


// Create doughnut

const popularityChart =
    document.getElementById("popularityChart");


new Chart(popularityChart, {

    type: "doughnut",

    data: {

        labels: topFoodNames,

        datasets: [{

            label: "Orders",

            data: topFoodOrders

        }]

    },

    options: {

        responsive: true,

        maintainAspectRatio: false,

        cutout: "58%",

        plugins: {

            legend: {

                position: "bottom",

                labels: {

                    padding: 10,

                    boxWidth: 12,

                    font: {

                        size: 11

                    }

                }

            },

            tooltip: {

                callbacks: {

                    label: function(context) {

                        return " " +
                            context.label +
                            ": " +
                            context.parsed +
                            " orders";

                    }

                }

            }

        }

    }

});


// =====================================================
// 5. FOOD AVAILABILITY
// =====================================================

const inventoryChart =
    document.getElementById("inventoryChart");


new Chart(inventoryChart, {

    type: "bar",

    data: {

        labels: [
            "Available",
            "Unavailable"
        ],

        datasets: [{

            label: "Food Items",

            data: [
                availableFood,
                unavailableFood
            ]

        }]

    },

    options: {

        responsive: true,

        maintainAspectRatio: false,

        plugins: {

            legend: {
                display: false
            },

            tooltip: {

                callbacks: {

                    label: function(context) {

                        return " " +
                            context.parsed.y +
                            " food items";

                    }

                }

            }

        },

        scales: {

            y: {

                beginAtZero: true,

                ticks: {

                    stepSize: 5

                },

                title: {

                    display: true,

                    text: "Number of Food Items"

                }

            }

        }

    }

});


// =====================================================
// 6. SMART INSIGHT - PEAK ORDERING TIME
// =====================================================

const maxOrders =
    Math.max(...ordersByTime);

const peakIndex =
    ordersByTime.indexOf(maxOrders);

const peakTime =
    orderTimes[peakIndex];


document.getElementById(
    "peakTimeInsight"
).textContent =

    "🔥 Peak ordering time: " +
    peakTime +
    " (" +
    maxOrders +
    " orders)";


// =====================================================
// 7. SMART INSIGHT - MOST POPULAR FOOD
// =====================================================

const maxFoodOrders =
    Math.max(...foodOrders);

const popularFoodIndex =
    foodOrders.indexOf(maxFoodOrders);

const popularFood =
    foodItems[popularFoodIndex];


document.getElementById(
    "popularFoodInsight"
).textContent =

    "🏆 Most ordered food: " +
    popularFood +
    " (" +
    maxFoodOrders +
    " orders)";


// =====================================================
// 8. SMART INSIGHT - FOOD AVAILABILITY
// =====================================================

document.getElementById(
    "lowStockInsight"
).textContent =

    "⚠️ Food availability: " +
    availableFood +
    " available, " +
    unavailableFood +
    " unavailable";


// =====================================================
// 9. RECENT ORDERS TABLE
// =====================================================

const ordersTableBody =
    document.getElementById("recentOrdersBody");


ordersTableBody.innerHTML = "";


recentOrders.forEach(order => {

    const row =
        document.createElement("tr");


    const formattedStatus =
        order.status.charAt(0).toUpperCase()
        +
        order.status.slice(1);


    row.innerHTML = `

        <td>#${order.id}</td>

        <td>${order.student}</td>

        <td>${order.food}</td>

        <td>
            ₹${order.amount.toLocaleString("en-IN")}
        </td>

        <td>

            <span class="status ${order.status}">

                ${formattedStatus}

            </span>

        </td>

    `;


    ordersTableBody.appendChild(row);

});


// =====================================================
// 10. CONSOLE INFORMATION
// =====================================================

console.log(
    "Smart Canteen Dashboard loaded successfully."
);

console.log(
    "Total Orders:",
    totalOrders
);

console.log(
    "Paid Revenue:",
    totalRevenue
);

console.log(
    "Pending Orders:",
    pendingOrders
);

console.log(
    "Available Food Items:",
    availableFood
);

console.log(
    "Unavailable Food Items:",
    unavailableFood
);