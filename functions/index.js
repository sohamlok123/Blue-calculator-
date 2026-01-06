/**
 * Smart Campus Ecosystem Backend
 * Author: Jules (Senior Backend Architect)
 * Framework: Firebase Cloud Functions (2nd Gen) + Node.js
 */

const { onDocumentCreated } = require("firebase-functions/v2/firestore");
const { onCall, onRequest, HttpsError } = require("firebase-functions/v2/https");
const { initializeApp } = require("firebase-admin/app");
const { getFirestore } = require("firebase-admin/firestore");
const logger = require("firebase-functions/logger");

// 1. CONSTANTS & SETUP
// Initialize the Firebase Admin SDK to interact with Firestore
initializeApp();
const db = getFirestore();

// Defined College Location (Lat 18.5204, Lng 73.8567)
const COLLEGE_LOCATION = {
    lat: 18.5204,
    lng: 73.8567
};

const ALLOWED_RADIUS = 100; // meters

/**
 * Helper function to calculate distance between two coordinates in meters.
 * Uses the Haversine formula.
 *
 * @param {number} lat1 - Latitude of point 1
 * @param {number} lon1 - Longitude of point 1
 * @param {number} lat2 - Latitude of point 2
 * @param {number} lon2 - Longitude of point 2
 * @returns {number} Distance in meters
 */
function calculateHaversineDistance(lat1, lon1, lat2, lon2) {
    const R = 6371e3; // Earth radius in meters
    const phi1 = lat1 * Math.PI / 180;
    const phi2 = lat2 * Math.PI / 180;
    const deltaPhi = (lat2 - lat1) * Math.PI / 180;
    const deltaLambda = (lon2 - lon1) * Math.PI / 180;

    const a = Math.sin(deltaPhi / 2) * Math.sin(deltaPhi / 2) +
              Math.cos(phi1) * Math.cos(phi2) *
              Math.sin(deltaLambda / 2) * Math.sin(deltaLambda / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    return R * c;
}

// 2. FEATURE 1: SMART ATTENDANCE (Firestore Trigger)
// Trigger: onDocumentCreated in AttendanceLogs/{docId}
// This function verifies if the student is within the college radius.
exports.verifyAttendance = onDocumentCreated("AttendanceLogs/{docId}", async (event) => {
    const snapshot = event.data;
    if (!snapshot) {
        console.log("No data associated with the event");
        return;
    }

    const data = snapshot.data();
    const studentLocation = data.location; // Expected format: { lat: number, lng: number }

    // Validate location data exists
    if (!studentLocation || typeof studentLocation.lat !== 'number' || typeof studentLocation.lng !== 'number') {
        console.log("Invalid or missing location data.");
        // Optionally mark as error in the document
        return snapshot.ref.update({ status: "Error: Invalid Location" });
    }

    // Calculate distance
    const distance = calculateHaversineDistance(
        studentLocation.lat,
        studentLocation.lng,
        COLLEGE_LOCATION.lat,
        COLLEGE_LOCATION.lng
    );

    console.log(`Calculated distance: ${distance} meters`);

    // Determine status based on distance
    let status = "Absent";
    if (distance <= ALLOWED_RADIUS) {
        status = "Present";
    }

    // Update the document with status and verification agent
    return snapshot.ref.update({
        status: status,
        verified_by: 'Jules Agent'
    });
});

// 3. FEATURE 2: SQUAD MANAGEMENT (Callable Function)
// Callable function to create a new study squad
exports.createSquad = onCall(async (request) => {
    // request.data contains the payload from the client
    const { topic, category, creatorName } = request.data;

    // Validate inputs
    if (!topic || !category || !creatorName) {
        throw new HttpsError("invalid-argument", "The function must be called with topic, category, and creatorName.");
    }

    try {
        // Create a new document in StudyGroups collection
        const result = await db.collection("StudyGroups").add({
            topic: topic,
            category: category,
            creatorName: creatorName,
            createdAt: new Date().toISOString(),
            members: 1
        });

        return {
            success: true,
            message: "Squad Created"
        };
    } catch (error) {
        console.error("Error creating squad:", error);
        throw new HttpsError("internal", "Unable to create squad.");
    }
});

// 4. FEATURE 3: AI DOUBT SOLVER (Callable Function - Mock)
// Callable function acting as a mock AI chat bot
exports.askJules = onCall((request) => {
    const { question } = request.data;

    if (!question) {
         throw new HttpsError("invalid-argument", "The function must be called with a 'question' argument.");
    }

    let answer = "That's a great question! I recommend asking your professor or creating a study squad.";
    const lowerQuestion = question.toLowerCase();

    // Simple keyword matching simulation
    if (lowerQuestion.includes("attendance")) {
        answer = "Attendance is automated via GPS.";
    } else if (lowerQuestion.includes("m1") || lowerQuestion.includes("math")) {
        answer = "Focus on Eigenvalues. Join a Math Squad!";
    }

    return {
        answer: answer,
        agent: "Jules v1"
    };
});

// 5. FEATURE 4: ASSIGNMENTS (Http Request)
// HTTP function to return mock deadlines
exports.getDeadlines = onRequest((req, res) => {
    const assignments = [
        { title: "Math Assignment - Due Tomorrow", dueDate: "Tomorrow", subject: "Math" },
        { title: "Physics Lab - Due Friday", dueDate: "Friday", subject: "Physics" }
    ];

    res.json(assignments);
});
