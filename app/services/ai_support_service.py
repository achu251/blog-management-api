
def get_ai_support_response(message: str) -> str:
    """
    Return a predefined AI-style support response
    based on the user's question.
    """

    text = message.lower().strip()

    # Create posts
    if (
        "create post" in text
        or "create a post" in text
        or "new post" in text
        or "add post" in text
        or "write post" in text
    ):
        return (
            "To create a post, log in to your account and open the "
            "Create Post section. Enter your title and content, add an "
            "image if needed, and submit the post."
        )

    # Edit posts
    if (
        "edit post" in text
        or "edit a post" in text
        or "update post" in text
        or "change my post" in text
    ):
        return (
            "To edit a post, open your own post and select the Edit option. "
            "Update the title, content, or image and save your changes."
        )

    # Delete posts
    if (
        "delete post" in text
        or "delete a post" in text
        or "remove post" in text
        or "remove a post" in text
    ):
        return (
            "You can delete your own post from the post management section. "
            "Open the post, choose Delete, and confirm the action."
        )

    # Subscriptions
    if (
        "subscription" in text
        or "subscribe" in text
        or "plan" in text
        or "renew" in text
    ):
        return (
            "You can manage your subscription from the Subscription section. "
            "You can view available plans, activate a subscription, and "
            "manage renewals from there."
        )

    # Billing
    if (
        "billing" in text
        or "payment" in text
        or "invoice" in text
        or "charge" in text
        or "transaction" in text
    ):
        return (
            "For billing-related information, open the Billing section of "
            "your account. You can review payment details and available "
            "billing information there."
        )

    # Profile
    if (
        "profile" in text
        or "account details" in text
        or "username" in text
        or "email address" in text
    ):
        return (
            "You can manage your profile from the Profile section. "
            "There you can review and update your account information."
        )

    # Dashboard analytics
    if (
        "dashboard" in text
        or "analytics" in text
        or "statistics" in text
        or "stats" in text
        or "views" in text
    ):
        return (
            "Your dashboard provides useful account analytics such as "
            "post statistics, comments, likes, and post views. "
            "Open the Dashboard section to view your activity."
        )

    # Comments
    if (
        "comment" in text
        or "comments" in text
    ):
        return (
            "You can add comments to posts by opening a post and using "
            "the comment section. Other users' comments can also appear "
            "on your posts."
        )

    # Likes
    if (
        "like" in text
        or "likes" in text
        or "unlike" in text
    ):
        return (
            "You can like a post using the Like option. If you have "
            "already liked it, you can use the same option to remove "
            "your like."
        )

    # General FAQ / help
    if (
        "help" in text
        or "faq" in text
        or "how does this work" in text
        or "what can you do" in text
    ):
        return (
            "I can help you with creating, editing, and deleting posts, "
            "subscriptions, billing, profile settings, dashboard analytics, "
            "comments, and likes. Ask me about any of these topics."
        )

    # Greeting
    if (
        text in {"hi", "hello", "hey", "hai", "good morning", "good afternoon"}
    ):
        return (
            "Hello! 👋 I'm your AI Support Assistant. "
            "You can ask me about posts, subscriptions, billing, "
            "your profile, dashboard analytics, comments, or likes."
        )

    # Fallback
    return (
        "I'm here to help with your blog account. You can ask me about "
        "creating, editing, or deleting posts, subscriptions, billing, "
        "profile settings, dashboard analytics, comments, or likes."
    )
