"""
InvestEz - CLI Entry Point

Conversational AI assistant for stock and mutual fund research.
"""

import sys
import click
from datetime import datetime

from config import ANTHROPIC_API_KEY
from agents.orchestrator import create_orchestrator
from storage.conversation_store import (
    create_conversation,
    save_conversation,
    load_conversation,
    list_conversations,
    auto_generate_name
)
from tools.kite import is_authenticated, authenticate


def print_welcome():
    """Print welcome message."""
    print("""
============================================================
                                                            
    InvestEz - Your Investment Research Assistant         
                                                            
    Get plain-language analysis of stocks and mutual funds  
                                                            
============================================================

Type 'help' for available commands or ask about any stock/fund.
Type 'exit' to save and quit.
""")


def print_status():
    """Print system status."""
    print("\nSystem Status:")
    print(f"   * Claude API: {'[OK] Connected' if ANTHROPIC_API_KEY else '[X] Not configured'}")
    print(f"   * Kite Connect: {'[OK] Authenticated' if is_authenticated() else '[ ] Not connected (fundamentals only)'}")
    print()


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """InvestEz - Conversational stock and mutual fund research."""
    if ctx.invoked_subcommand is None:
        # Default: start new conversation
        start_conversation()


@cli.command()
def new():
    """Start a new conversation."""
    start_conversation()


@cli.command()
def conversations():
    """List recent conversations."""
    convs = list_conversations(limit=10)
    
    if not convs:
        print("\nNo saved conversations yet.\n")
        return
    
    print("\nRecent Conversations:")
    print("-" * 60)
    
    for i, conv in enumerate(convs, 1):
        name = conv.get('name', 'Unnamed')
        msg_count = conv.get('message_count', 0)
        session_id = conv.get('session_id', '')
        print(f"{i}. {name}")
        print(f"   Messages: {msg_count} | ID: {session_id[:30]}...")
    
    print("\nUse 'python main.py resume <session_id>' to continue a conversation.\n")


@cli.command()
@click.argument('session_id')
def resume(session_id: str):
    """Resume a previous conversation."""
    conversation = load_conversation(session_id)
    
    if not conversation:
        print(f"\n[X] Conversation not found: {session_id}")
        print("Use 'python main.py conversations' to list available conversations.\n")
        return
    
    print(f"\nResuming: {conversation.name}")
    print(f"   Messages: {len(conversation.messages)}")
    print(f"   Started: {conversation.created_at.strftime('%Y-%m-%d %H:%M')}")
    
    # Show last few messages for context
    if conversation.messages:
        print("\n-- Recent context --")
        for msg in conversation.messages[-4:]:
            role = "You" if msg.role == "user" else "InvestEz"
            content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
            print(f"   {role}: {content}")
        print("--------------------\n")
    
    run_conversation_loop(conversation)


@cli.command()
def auth():
    """Authenticate with Zerodha Kite Connect."""
    print("\n--- Kite Connect Authentication ---")
    print("-" * 40)
    
    if is_authenticated():
        print("Already authenticated!")
        return
    
    if authenticate():
        print("\n[OK] Authentication successful!")
    else:
        print("\n[FAILED] Authentication failed. Try again.")


def start_conversation():
    """Start a new conversation session."""
    print_welcome()
    print_status()
    
    conversation = create_conversation()
    run_conversation_loop(conversation)


def run_conversation_loop(conversation):
    """Main conversation loop."""
    orchestrator = create_orchestrator(conversation)
    first_message = True
    
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
            
            # Check for exit
            if user_input.lower() in ['exit', 'quit', 'bye', 'q']:
                # Save conversation before exiting
                if len(conversation.messages) > 0:
                    # Auto-generate name from first message if still default
                    if conversation.name.startswith("Conversation"):
                        first_query = conversation.get_last_user_query()
                        if first_query:
                            conversation.name = auto_generate_name(first_query)
                    
                    save_path = save_conversation(conversation)
                    print(f"\n[Saved] Conversation saved: {conversation.name}")
                
                print("\nGoodbye! Happy investing!\n")
                break
            
            # Add user message to conversation
            conversation.add_user_message(user_input)
            
            # Process query
            print("\nThinking...", end="", flush=True)
            response, agent, tools = orchestrator.process_query(user_input)
            print("\r" + " " * 20 + "\r", end="")  # Clear "Thinking..."
            
            # Display response
            print(f"\nInvestEz: {response}")
            
            # Add response to conversation
            conversation.add_assistant_message(response, agent=agent, tools_used=tools)
            
            # Auto-save periodically
            if len(conversation.messages) % 10 == 0:
                save_conversation(conversation)
            
            # Generate name after first meaningful exchange
            if first_message and len(conversation.messages) >= 2:
                first_query = conversation.get_last_user_query()
                if first_query:
                    conversation.name = auto_generate_name(first_query)
                first_message = False
                
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print("\n\nInterrupted. Saving conversation...")
            if len(conversation.messages) > 0:
                save_conversation(conversation)
                print(f"[Saved] {conversation.name}")
            print("Goodbye!\n")
            break
        except Exception as e:
            print(f"\n[Error] {e}")
            print("Please try again or type 'exit' to quit.\n")


if __name__ == "__main__":
    cli()
