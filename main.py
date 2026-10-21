import argparse
import sys
import os
from pathlib import Path

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from src.agent import CreatorAgent
from src.config import DEFAULT_VOICES

console = Console(safe_box=True)

def print_banner():
    banner = """
  ======================================================
             AI CREATOR AGENT (PRO EDITION)             
     Automated Video Creation * Captions * Voice-Over   
  ======================================================
    """
    console.print(Panel(banner, style="bold cyan", border_style="cyan"))

def run_scenario_audio(agent: CreatorAgent):
    console.print("\n[bold yellow]=== SCENARIO 1: Create Video from Audio File ===[/bold yellow]")
    audio_path = Prompt.ask("[cyan]Enter path to your audio file (.mp3 / .wav / .m4a)[/cyan]")
    audio_file = Path(audio_path.strip("\"'"))

    if not audio_file.exists():
        console.print(f"[bold red]Error: File not found at {audio_file}[/bold red]")
        return

    category_choice = Prompt.ask(
        "[cyan]Select video format[/cyan]",
        choices=["reel", "video"],
        default="reel",
    )
    console.print(f"\n[green]Starting video generation for {category_choice}...[/green]")
    agent.create_from_audio(audio_path=audio_file, category=category_choice)

def run_scenario_doc(agent: CreatorAgent):
    console.print("\n[bold yellow]=== SCENARIO 2: Create Video from Document / Notes ===[/bold yellow]")
    input_type = Prompt.ask(
        "[cyan]Do you have a file path or direct text?[/cyan]",
        choices=["file", "text"],
        default="file",
    )

    if input_type == "file":
        doc_path = Prompt.ask("[cyan]Enter document file path (.txt / .md / etc.)[/cyan]")
        doc_file = Path(doc_path.strip("\"'"))
        if not doc_file.exists():
            console.print(f"[bold red]Error: File not found at {doc_file}[/bold red]")
            return
        content = doc_file.read_text(encoding="utf-8", errors="ignore")
    else:
        content = Prompt.ask("[cyan]Paste your notes or campaign briefing[/cyan]")

    category_choice = Prompt.ask(
        "[cyan]Select video format[/cyan]",
        choices=["reel", "video"],
        default="reel",
    )

    target_duration = 60 if category_choice == "reel" else 180
    duration_input = Prompt.ask(
        f"[cyan]Target duration in seconds[/cyan]",
        default=str(target_duration),
    )
    try:
        target_duration = int(duration_input)
    except ValueError:
        pass

    console.print("\n[bold cyan]Available Voices:[/bold cyan]")
    voice_keys = list(DEFAULT_VOICES.keys())
    for idx, vk in enumerate(voice_keys, start=1):
        console.print(f"  {idx}. {vk.replace('_', ' ').title()} ({DEFAULT_VOICES[vk]})")

    voice_idx = Prompt.ask("[cyan]Choose voice preset (number)[/cyan]", default="1")
    try:
        chosen_voice_key = voice_keys[int(voice_idx) - 1]
        agent.voice_engine.voice = DEFAULT_VOICES[chosen_voice_key]
    except Exception:
        agent.voice_engine.voice = DEFAULT_VOICES["english_male"]

    console.print(f"\n[green]Generating complete video campaign ({category_choice}, {target_duration}s)...[/green]")
    agent.create_from_document(
        doc_or_text=content,
        category=category_choice,
        target_duration=target_duration,
    )

def run_quick_demo(agent: CreatorAgent):
    console.print("\n[bold yellow]=== QUICK DEMO: Generating Sample Creator Reel ===[/bold yellow]")
    demo_notes = (
        "Here is the secret of high performance creator agents. "
        "With automated visual synthesis, instant studio voice-overs, "
        "and karaoke highlighted captions, anyone can build viral content in seconds."
    )
    console.print(f"[cyan]Demo Script:[/cyan] [italic]{demo_notes}[/italic]\n")
    agent.create_from_document(
        doc_or_text=demo_notes,
        category="reel",
        target_duration=20,
        output_name="demo_viral_reel.mp4",
    )

def main():
    parser = argparse.ArgumentParser(description="AI Creator Agent CLI")
    parser.add_argument("--scenario", choices=["audio", "doc", "demo"], help="Directly trigger scenario")
    parser.add_argument("--input", help="Path to audio file or doc file")
    parser.add_argument("--category", choices=["reel", "video"], default="reel", help="Format of video")
    parser.add_argument("--duration", type=int, default=60, help="Target duration in seconds")
    parser.add_argument("--voice", help="Edge TTS voice name")
    args = parser.parse_args()

    print_banner()

    agent = CreatorAgent(
        voice=args.voice,
        whisper_model="base",
    )

    if args.scenario == "demo":
        run_quick_demo(agent)
        return
    elif args.scenario == "audio" and args.input:
        agent.create_from_audio(audio_path=args.input, category=args.category)
        return
    elif args.scenario == "doc" and args.input:
        agent.create_from_document(
            doc_or_text=args.input,
            category=args.category,
            target_duration=args.duration,
        )
        return

    # Interactive menu
    while True:
        console.print("\n[bold cyan]Choose an action:[/bold cyan]")
        console.print("  [1] 🎵 Create Video from Audio File (Audio -> Captions & Visuals)")
        console.print("  [2] 📄 Create Video from Notes/Docs (Doc -> Script + Voice + Visuals + Captions)")
        console.print("  [3] ⚡ Run Quick Demo Reel (End-to-end verification)")
        console.print("  [4] 🚪 Exit")

        choice = Prompt.ask("\n[bold green]Enter your choice[/bold green]", choices=["1", "2", "3", "4"], default="3")

        if choice == "1":
            run_scenario_audio(agent)
        elif choice == "2":
            run_scenario_doc(agent)
        elif choice == "3":
            run_quick_demo(agent)
        elif choice == "4":
            console.print("[yellow]Bhai, see you soon! Happy creating! 👋[/yellow]")
            break

if __name__ == "__main__":
    main()
