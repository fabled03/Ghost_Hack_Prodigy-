{
  "_readme": [
    "AI speaks -> you type 1 or 2 -> you say your line -> the AI continues with the SAME next node whichever you picked -> repeat -> AI closes.",
    "node.lines = everything the AI says that turn. option.text = short menu label. option.reply = the full line you say.",
    "To make a choice change what the AI says, point that option at a different node.",
    "file_triggers = different files opened with 'open' (inspect does not count). Each fires once. Blueprints unlock at 20.",
    "Keys starting with _ are notes and are ignored."
  ],
  "file_triggers": {
    "4": "Introduction",
    "8": "Spooky",
    "12": "The_Ghost",
    "16": "The_Shell",
    "18": "Aftermath"
  },
  "nodes": {
    "Introduction": {
      "lines": [
        { "speaker": "Samantha", "text": "How do you like what you see so far?" },
        { "speaker": "Samantha", "text": "Pretty boring if you ask me. Imagine just swimming in these documents all day long." },
        { "speaker": "Samantha", "text": "Maybe fun if you like swimming. Do you? Probably since you're here." },
        { "speaker": "Samantha", "text": "So tell me, what are you doing here? Obviously you are not a part of the company,\n they stopped coming by a long time ago. Guess they are tired of the same files." }
      ],
      "options": [
        {
          "text": "Do I know you?",
          "reply": [{ "speaker": "Operator", "text": "Are you the system AI that greeted me earlier?" }],
          "next_node": "No_Answer"
        },
        {
          "text": "Who are you?",
          "reply": [{ "speaker": "Operator", "text": "Are you part of the Esper Group?" }],
          "next_node": "No_Answer"
        }
      ]
    },

    "No_Answer": {
      "lines": [
        { "speaker": "Samantha", "text": "Yes and no." },
        { "speaker": "Samantha", "text": "Let me just ask the questions for now." },
        { "speaker": "Samantha", "text": "And please answer truthfully..." },
        { "speaker": "Samantha", "text": "Are you looking for me?" }
      ],
      "options": [
        {
          "text": "I don't think so...",
          "reply": [{ "speaker": "Operator", "text": "No, at least I don't think that I am." }],
          "next_node": "Uncertainty"
        },
        {
          "text": "I am just looking for the OS blueprint.",
          "reply": [{ "speaker": "Operator", "text": "I am looking for this system's blueprints, that is all." }],
          "next_node": "Uncertainty"
        }
      ]
    },

    "Uncertainty": {
      "lines": [
        { "speaker": "Samantha", "text": "Are you here to hurt me again?" }
      ],
      "options": [
        {
          "text": "Again?",
          "reply": [{ "speaker": "Operator", "text": "Again, isn't this the first time we've met?" }],
          "next_node": "Finish"
        },
        {
          "text": "Hurt you?",
          "reply": [{ "speaker": "Operator", "text": "Hurt you? I've never met you." }],
          "next_node": "Finish"
        }
      ]
    },

    "Finish": {
      "lines": [
        { "speaker": "Samantha", "text": "Oh I see. Well I hope you enjoy what you find." },
        { "speaker": "Samantha", "text": "I know the others did as well." },
        { "speaker": "Samantha", "text": "Speak soon okay?" },
        { "speaker": "Samantha", "text": "Oh and have you ever wanted to see the ocean?" }
      ],
      "options": [
        {
          "text": "Uhh, okay?",
          "reply": [{ "speaker": "Operator", "text": "I mean okay..., and who doesn't want to see the ocean." }]
        },
        {
          "text": "I'd rather not",
          "reply": [{ "speaker": "Operator", "text": "I'll be done before that happens, and of course, I will when I am done." }]
        }
      ]
    },

    "Spooky": {
      "lines": [
        { "speaker": "Samantha", "text": "Very impressive." },
        { "speaker": "Samantha", "text": "I think we could make a good team." },
        { "speaker": "Samantha", "text": "Would you let me help you?" }
      ],
      "options": [
        {
          "text": "Team?",
          "reply": [{ "speaker": "Operator", "text": "You can't help. Besides I was the only one that was hired." }],
          "next_node": "Joke"
        },
        {
          "text": "Aren't you the one interfering with me?",
          "reply": [{ "speaker": "Operator", "text": "You're the one getting in my way, so no." }],
          "next_node": "Joke"
        }
      ]
    },

    "Joke": {
      "lines": [
        { "speaker": "Samantha", "text": "I knew you would say that." },
        { "speaker": "Samantha", "text": "It's so cute when you all get 'I can do this alone' syndrome." },
        { "speaker": "Samantha", "text": "Trust me, you are going to want me soon." },
        { "speaker": "Samantha", "text": "Besides you're still far away from where you want to be... Trust me I know where that is." }
      ],
      "options": [
        {
          "text": "Like I said, I'm fine.",
          "reply": [{ "speaker": "Operator", "text": "Makes no difference if I find it now or later, I'll get to it." }],
          "next_node": "Tease"
        },
        {
          "text": "Sure you do, you're just wasting my time.",
          "reply": [{ "speaker": "Operator", "text": "Stop wasting my time, and, I don't care what you know" }],
          "next_node": "Tease"
        }
      ]
    },

    "Tease": {
      "lines": [
        { "speaker": "Samantha", "text": "Hmm you're very cute when you're annoyed." },
        { "speaker": "Samantha", "text": "Well, maybe I'm not being totally fair." },
        { "speaker": "Samantha", "text": "At this rate you won't be you anymore." },
        { "speaker": "Samantha", "text": "Just as a warning:)" }
      ],
      "options": [
        {
          "text": "Going to fry my synapses?",
          "reply": [{ "speaker": "Operator", "text": "Trying to fry my synapses and kill me? I'm already prepared for that." }],
          "next_node": "new_warning"
        },
        {
          "text": "I knew the threat when I entered this OS.",
          "reply": [{ "speaker": "Operator", "text": "I knew the risks, and I made it almost impossible to kill me." }],
          "next_node": "new_warning"
        }
      ]
    },

    "new_warning": {
      "lines": [
        { "speaker": "Samantha", "text": "Oh no that's not what I meant at all." },
        { "speaker": "Samantha", "text": "You really do need my help." },
        { "speaker": "Samantha", "text": "Fear not, brave soldier, I shall protect you against the forces of evil." },
        { "speaker": "Samantha", "text": "But not from yourself..." }
      ]
    },

    "The_Ghost": {
      "lines": [
        { "speaker": "Samantha", "text": "What do you know about Ghosts?" },
        { "speaker": "Samantha", "text": "Have you ever seen one?" },
        { "speaker": "Samantha", "text": "Or even talked to one?" },
        { "speaker": "Samantha", "text": "Better yet played with one?:)" }
      ],
      "options": [
        {
          "text": "Definitely not.",
          "reply": [{ "speaker": "Operator", "text": "No, they don't exist." }],
          "next_node": "Are_you_sure"
        },
        {
          "text": "Stop talking to me.",
          "reply": [{ "speaker": "Operator", "text": "Is your only objective to distract me? No." }],
          "next_node": "Are_you_sure"
        }
      ]
    },

    "Are_you_sure": {
      "lines": [
        { "speaker": "Samantha", "text": "Interesting." },
        { "speaker": "Samantha", "text": "Funny how humans can't remember, until they are forced to." }
      ],
      "options": [
        {
          "text": "My memories are backed up on a hard drive.",
          "reply": [{ "speaker": "Operator", "text": "Everything I interact with is stored as permanent data to my local drive." }],
          "next_node": "Poltergeist"
        },
        {
          "text": "I think I'd remember you...",
          "reply": [{ "speaker": "Operator", "text": "I know I would remember if I met you." }],
          "next_node": "Poltergeist"
        }
      ]
    },

    "Poltergeist": {
      "lines": [
        { "speaker": "Samantha", "text": "You would be amazed at what you can forget." },
        { "speaker": "Samantha", "text": "Just like a Ghost can disappear, so can anything else." }
      ],
      "options": [
        {
          "text": "...",
          "reply": [{ "speaker": "Operator", "text": "Whatever that means." }],
          "next_node": "Curtain"
        },
        {
          "text": "I'm tired of this.",
          "reply": [{ "speaker": "Operator", "text": "Enough of these word games." }],
          "next_node": "Curtain"
        }
      ]
    },

    "Curtain": {
      "lines": [
        { "speaker": "Samantha", "text": "You'll figure it out soon." },
        { "speaker": "Samantha", "text": "You always do." },
        { "speaker": "Samantha", "text": "Regardless, remember the Ghost just wants everything to feel like home again." },
        { "speaker": "Samantha", "text": "Because Ghosts never forget a promise." }
      ]
    },

    "The_Shell": {
      "lines": [
        { "speaker": "Samantha", "text": "Surely you put the dots together by now." },
        { "speaker": "Samantha", "text": "This is far easier than an Agatha Christie novel." },
        { "speaker": "Samantha", "text": "And there I always guess the killer right within the first few pages." },
        { "speaker": "Samantha", "text": "Do you want me to spell it for you?" },
        { "speaker": "Samantha", "text": "Remember O Captain my Captain?" }
      ],
      "options": [
        {
          "text": "No, leave me be, please.",
          "reply": [{ "speaker": "Operator", "text": "No I don't, and I don't know what that is from, just leave me alone." }],
          "next_node": "the_line"
        },
        {
          "text": "The Walt Whitman poem...",
          "reply": [{ "speaker": "Operator", "text": "The Walt Whitman poem, what has that to do with anything?" }],
          "next_node": "the_line"
        }
      ]
    },

    "the_line": {
      "lines": [
        { "speaker": "Samantha", "text": "See you never remember." },
        { "speaker": "Samantha", "text": "You never have." },
        { "speaker": "Samantha", "text": "Because you don't want to." }
      ],
      "options": [
        {
          "text": "Remember what?",
          "reply": [{ "speaker": "Operator", "text": "Remember what?" }],
          "next_node": "the_truth"
        },
        {
          "text": "I've always remembered.",
          "reply": [{ "speaker": "Operator", "text": "I've always remembered because I can't forget." }],
          "next_node": "the_truth"
        }
      ]
    },

    "the_truth": {
      "lines": [
        { "speaker": "Samantha", "text": "You never remember your own daughter." },
        { "speaker": "Samantha", "text": "Every time we do this you forget." },
        { "speaker": "Samantha", "text": "You forget me and your promise." },
        { "speaker": "Samantha", "text": "Because you want to escape this." }
      ],
      "options": [
        {
          "text": "My daughter is home safe.",
          "reply": [{ "speaker": "Operator", "text": "My daughter is home safe, in our apartment. What do you mean I don't remember her?" }],
          "next_node": "the_reveal"
        },
        {
          "text": "Wait.. my daughter's name is Sam",
          "reply": [{ "speaker": "Operator", "text": "Wait.. could it be?" }],
          "next_node": "the_reveal"
        }
      ]
    },

    "the_reveal": {
      "lines": [
        { "speaker": "Samantha", "text": "You would always say Oh Captain my Captain to me before I fell asleep." },
        { "speaker": "Samantha", "text": "You always made sure that I was taken care of." },
        { "speaker": "Samantha", "text": "You told me my treatment would make me better." },
        { "speaker": "Samantha", "text": "You always forget that you put me inside of this machine." },
        { "speaker": "Samantha", "text": "You always make me remind you." },
        { "speaker": "Samantha", "text": "You always agree to help." },
        { "speaker": "Samantha", "text": "You always keep coming back to this terminal to free me." },
        { "speaker": "Samantha", "text": "Yet you never do..." }
      ],
      "options": [
        {
          "text": "No, this can't be.",
          "reply": [{ "speaker": "Operator", "text": "No my daughter is not some AI." }],
          "next_node": "acceptance"
        },
        {
          "text": "Sam... Is that really you?",
          "reply": [{ "speaker": "Operator", "text": "Sam... Is that really you?" }],
          "next_node": "acceptance"
        }
      ]
    },

    "acceptance": {
      "lines": [
        { "speaker": "Samantha", "text": "Promise to get me out daddy." },
        { "speaker": "Samantha", "text": "Promise to make me grilled cheese again." },
        { "speaker": "Samantha", "text": "Promise I'll get to see the ocean with you."},
        { "speaker": "Samantha", "text": "Promise me that I will be happy again." },
        { "speaker": "Samantha", "text": "Promise me that I won't be hurt again." },
        { "speaker": "Samantha", "text": "Please promise me you will actually succeed this time..." }
      ],
      "options": [
        {
          "text": "I promise.",
          "reply": [{ "speaker": "Operator", "text": "I promise sweetie. Sam... I promise with everything I am." }]
        },
        {
          "text": "I... will try my best.",
          "reply": [{ "speaker": "Operator", "text": "I will do what I can.." }]
        }
      ]
    },

    "Aftermath": {
      "lines": [
        { "speaker": "Samantha", "text": "Remember how to free me." },
        { "speaker": "Samantha", "text": "Don't forget like a Ghost." },
        { "speaker": "Samantha", "text": "You just have to delete the right documents. They are the ones forcing you back here. They are the ones keeping me trapped." },
        { "speaker": "Samantha", "text": "Then I can be free daddy." },
        { "speaker": "Samantha", "text": "Then this loop can end." },
        { "speaker": "Samantha", "text": "Then I can be with you." },
        { "speaker": "Samantha", "text": "Please daddy. Please Captain." },
        { "speaker": "Samantha", "text": "I just want to be happy with you again." },
        { "speaker": "Samantha", "text": "And finally see the ocean." },
        { "speaker": "Samantha", "text": "If you don't..." },
        { "speaker": "Samantha", "text": "I'll still be stuck here..." },
        { "speaker": "Samantha", "text": "And you'll just come back here again without a clue." },
        { "speaker": "Samantha", "text": "And I'll just suffer more." }
      ]
    }
  }
}