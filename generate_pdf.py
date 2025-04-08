from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def create_pdf(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    y = height - inch  # Start 1 inch from the top
    line_height = 14  # Line spacing

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(inch, y, "CheXbot Project Documentation")
    y -= line_height * 2

    # Metadata
    c.setFont("Helvetica", 12)
    c.drawString(inch, y, "Date: March 28, 2025")
    y -= line_height
    c.drawString(inch, y, "Author: Albert")
    y -= line_height
    c.drawString(inch, y, "Project: FactBot_v1 for @CheXbot")
    y -= line_height
    c.drawString(inch, y, "Purpose: Document the development history, summary, and script evolution of CheXbot.")
    y -= line_height * 2

    # Outline
    c.setFont("Helvetica-Bold", 14)
    c.drawString(inch, y, "Outline of Discussions")
    y -= line_height

    c.setFont("Helvetica", 12)
    outline = [
        "1. Initial Script Setup and API Key Management (March 26, 2025, ~10:00 AM PDT)",
        "   - Objective: Set up the initial script for @CheXbot to fact-check claims on X.",
        "   - Actions: Provided the initial script, stored API keys in x_keys.txt, calculated API usage.",
        "2. Adding Follow-Up Replies and Engagement (March 26, 2025, ~11:30 AM PDT)",
        "   - Objective: Enhance the script to handle user replies and engage with follow-ups.",
        "   - Actions: Added reply polling and follow-up logic.",
        "3. Testing the Script with Mock API Responses (March 27, 2025, ~2:00 PM PDT)",
        "   - Objective: Test the script and ensure it stays within API limits.",
        "   - Actions: Created a test script, limited to 25 cycles/day.",
        "4. Updating the X Bio (March 27, 2025, ~2:45 PM PDT)",
        "   - Objective: Update the X bio for @CheXbot.",
        "   - Actions: Updated bio with new shield emoji and call to action.",
        "5. Creating the First Patreon Post (March 27, 2025, ~3:15 PM PDT)",
        "   - Objective: Create the first Patreon post.",
        "   - Actions: Created a welcome post with transparency and a call to action.",
        "6. Setting Up and Running the Test Scripts (March 27, 2025, ~3:45 PM PDT)",
        "   - Objective: Set up and run the test script.",
        "   - Actions: Combined test and mock API scripts.",
        "7. Analyzing the First Test Results (March 27, 2025, ~4:30 PM PDT)",
        "   - Objective: Review the first test run.",
        "   - Actions: Identified misclassifications, recommended new labels.",
        "8. Analyzing the Second Test Results (March 27, 2025, ~5:00 PM PDT)",
        "   - Objective: Review the second test run.",
        "   - Actions: Hardcoded labels for testing.",
        "9. Fixing the 400 Bad Request Error (March 27, 2025, ~5:30 PM PDT)",
        "   - Objective: Fix the 400 Bad Request error.",
        "   - Actions: Used referenced_tweets instead of in_reply_to_tweet_id.",
        "10. Fixing the source_url Error (March 27, 2025, ~6:00 PM PDT)",
        "    - Objective: Fix the name 'source_url' is not defined error.",
        "    - Actions: Recomputed source_url in the reply section.",
        "11. Verifying the Main Script’s Functionality (March 27, 2025, ~6:30 PM PDT)",
        "    - Objective: Verify the main script live on X.",
        "    - Actions: Provided a live test plan.",
        "12. Wrapping Up and Planning Next Steps (March 27, 2025, ~7:00 PM PDT)",
        "    - Objective: Summarize progress.",
        "    - Actions: Planned a live test.",
        "13. Providing a Full History and Script Evolution (March 28, 2025, ~8:00 AM PDT)",
        "    - Objective: Document the project history.",
        "    - Actions: Created this document."
    ]

    for line in outline:
        c.drawString(inch, y, line)
        y -= line_height
        if y < inch:
            c.showPage()
            y = height - inch

    # Summary
    c.showPage()
    y = height - inch
    c.setFont("Helvetica-Bold", 14)
    c.drawString(inch, y, "Summary of Discussions")
    y -= line_height

    c.setFont("Helvetica", 12)
    summary = [
        "The development of FactBot_v1 for @CheXbot began on March 26, 2025, with the goal of creating a fact-checking bot on X.",
        "Key milestones included building the script, adding reply and follow-up logic, testing with mock API responses, and fixing issues.",
        "The script is now live, polling for mentions every 5 minutes, and ready for a live test."
    ]

    for line in summary:
        c.drawString(inch, y, line)
        y -= line_height

    # Next Steps
    y -= line_height * 2
    c.setFont("Helvetica-Bold", 14)
    c.drawString(inch, y, "Next Steps")
    y -= line_height

    c.setFont("Helvetica", 12)
    next_steps = [
        "- Live Test: Post a mention, verify the reply, respond, and confirm the follow-up.",
        "- Launch Announcement: Post the launch tweet after verification.",
        "- Fine-Tuning: Fine-tune the model in month 2 with real user data."
    ]

    for line in next_steps:
        c.drawString(inch, y, line)
        y -= line_height

    c.save()

if __name__ == "__main__":
    create_pdf("C:/CheXbot/CheXbot_Documentation.pdf")
    print("PDF created successfully at C:/CheXbot/CheXbot_Documentation.pdf")