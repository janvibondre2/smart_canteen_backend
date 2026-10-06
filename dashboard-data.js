// =====================================================
// SMART CANTEEN - REAL DATA
// Data processed from the uploaded CSV files
// =====================================================


// =====================================================
// BASIC DASHBOARD COUNTS
// =====================================================

const totalOrders = 61;


// Paid payments only
const totalRevenue = 7165;


const pendingOrders = 11;


// FoodItems.availability = 0
const unavailableFoodItems = 1;


// =====================================================
// ORDERS BY FOOD ITEM
// Source:
// OrderItems.xls + FoodItems.xls
// =====================================================

const foodItems = [
    "Masala Chai",
    "Chole Bhature",
    "Idli Sambar",
    "Filter Coffee",
    "Fruit Custard",
    "Upma",
    "Brownie",
    "Veg Puff",
    "Aloo Paratha",
    "Samosa",
    "Bread Omelette",
    "Cold Coffee",
    "Veg Sandwich",
    "French Fries",
    "Poha",
    "Gulab Jamun",
    "Veg Biryani",
    "Fresh Lime Water",
    "Veg Thali",
    "Lemon Soda",
    "Mango Shake",
    "Spring Roll",
    "Paneer Butter Masala",
    "Ice Cream Cup"
];


const foodOrders = [
    18,
    17,
    17,
    15,
    15,
    12,
    12,
    12,
    11,
    10,
    10,
    9,
    9,
    9,
    9,
    9,
    8,
    7,
    6,
    6,
    5,
    5,
    3,
    3
];


// =====================================================
// ORDERS BY TIME
// Source:
// Orders.xls → order_date
// =====================================================

const orderTimes = [
    "4 PM",
    "9 PM"
];


const ordersByTime = [
    1,
    60
];


// =====================================================
// FOOD AVAILABILITY
// Source:
// FoodItems.xls → availability
// =====================================================

const availableFood = 24;

const unavailableFood = 1;


const unavailableFoodNames = [
    "Dal Khichdi"
];


// =====================================================
// PAYMENT METHODS
// Source:
// Payments.xls
//
// Only PAID payments are included.
// =====================================================

const paymentMethods = [
    "Card",
    "Cash",
    "UPI"
];


const paymentAmounts = [
    2712,
    2259,
    2194
];


// =====================================================
// ORDER STATUS
// Source:
// Orders.xls
// =====================================================

const orderStatuses = [
    "Completed",
    "Preparing",
    "Pending"
];


const orderStatusCounts = [
    37,
    13,
    11
];


// =====================================================
// CATEGORY-WISE ORDERS
// Source:
// Categories.xls
// FoodItems.xls
// OrderItems.xls
// =====================================================

const categories = [
    "Breakfast",
    "Beverages",
    "Desserts",
    "Snacks",
    "Lunch"
];


const categoryOrders = [
    68,
    60,
    39,
    36,
    34
];


// =====================================================
// RECENT ORDERS
// Source:
// Orders + Users + OrderItems + FoodItems
// =====================================================

const recentOrders = [

    {
        id: 61,
        student: "Sneha Kulkarni",
        food: "Gulab Jamun × 1, Filter Coffee × 1",
        amount: 50,
        status: "completed"
    },

    {
        id: 60,
        student: "Rohan Verma",
        food: "Fruit Custard × 3, Chole Bhature × 3, French Fries × 2",
        amount: 390,
        status: "completed"
    },

    {
        id: 59,
        student: "Riya Bansal",
        food: "Veg Puff × 3, Lemon Soda × 1, Upma × 2, Veg Sandwich × 2",
        amount: 209,
        status: "completed"
    },

    {
        id: 58,
        student: "Rahul Bhatt",
        food: "Filter Coffee × 3, Aloo Paratha × 1",
        amount: 95,
        status: "pending"
    },

    {
        id: 57,
        student: "Kavya Nair",
        food: "Aloo Paratha × 1, Spring Roll × 1",
        amount: 85,
        status: "completed"
    }

];