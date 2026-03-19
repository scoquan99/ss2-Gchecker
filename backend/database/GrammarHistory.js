const mongoose = require("mongoose");

const GrammarHistorySchema = new mongoose.Schema({

    originalText: String,

    errors: [
        {
            type: String,
            original: String,
            suggestion: String,
            explanation: String
        }
    ],

    score: Number,

    createdAt: {
        type: Date,
        default: Date.now
    }

});

module.exports = mongoose.model("GrammarHistory", GrammarHistorySchema);