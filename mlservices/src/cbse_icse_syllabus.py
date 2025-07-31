"""
CBSE/ICSE Board Syllabus and Paper Generation System
Provides board-specific content for Indian schools
"""

import random
from typing import Dict, List, Any

class CBSEICSESyllabus:
    def __init__(self):
        # CBSE Syllabus Structure - Classes 1-12
        self.cbse_syllabus = {
            "Mathematics": {
                "Class 1": {
                    "units": ["Numbers", "Addition", "Subtraction", "Shapes", "Measurement"],
                    "topics": {
                        "Numbers": ["Counting 1-100", "Number Names", "Place Value", "Number Patterns"],
                        "Addition": ["Addition up to 20", "Addition Stories", "Mental Addition"],
                        "Subtraction": ["Subtraction up to 20", "Subtraction Stories", "Mental Subtraction"],
                        "Shapes": ["2D Shapes", "3D Shapes", "Patterns", "Symmetry"],
                        "Measurement": ["Length", "Weight", "Capacity", "Time", "Money"]
                    }
                },
                "Class 2": {
                    "units": ["Numbers", "Addition", "Subtraction", "Multiplication", "Shapes", "Measurement"],
                    "topics": {
                        "Numbers": ["Numbers up to 1000", "Place Value", "Number Patterns", "Skip Counting"],
                        "Addition": ["Addition up to 100", "Addition with Carrying", "Mental Addition"],
                        "Subtraction": ["Subtraction up to 100", "Subtraction with Borrowing", "Mental Subtraction"],
                        "Multiplication": ["Multiplication Tables 2-10", "Multiplication Stories"],
                        "Shapes": ["2D and 3D Shapes", "Patterns", "Symmetry", "Tangrams"],
                        "Measurement": ["Length", "Weight", "Capacity", "Time", "Money"]
                    }
                },
                "Class 3": {
                    "units": ["Numbers", "Addition", "Subtraction", "Multiplication", "Division", "Shapes", "Measurement"],
                    "topics": {
                        "Numbers": ["Numbers up to 10000", "Place Value", "Number Patterns", "Roman Numerals"],
                        "Addition": ["Addition up to 1000", "Addition with Carrying", "Mental Addition"],
                        "Subtraction": ["Subtraction up to 1000", "Subtraction with Borrowing", "Mental Subtraction"],
                        "Multiplication": ["Multiplication Tables 2-12", "Multiplication with Carrying"],
                        "Division": ["Division Facts", "Division with Remainder", "Mental Division"],
                        "Shapes": ["2D and 3D Shapes", "Patterns", "Symmetry", "Area and Perimeter"],
                        "Measurement": ["Length", "Weight", "Capacity", "Time", "Money"]
                    }
                },
                "Class 4": {
                    "units": ["Numbers", "Addition", "Subtraction", "Multiplication", "Division", "Fractions", "Geometry", "Measurement"],
                    "topics": {
                        "Numbers": ["Numbers up to 100000", "Place Value", "Number Patterns", "Roman Numerals"],
                        "Addition": ["Addition up to 10000", "Addition with Carrying", "Mental Addition"],
                        "Subtraction": ["Subtraction up to 10000", "Subtraction with Borrowing", "Mental Subtraction"],
                        "Multiplication": ["Multiplication Tables 2-12", "Multiplication with Carrying"],
                        "Division": ["Division Facts", "Division with Remainder", "Mental Division"],
                        "Fractions": ["Fractions", "Equivalent Fractions", "Comparing Fractions"],
                        "Geometry": ["2D and 3D Shapes", "Angles", "Symmetry", "Area and Perimeter"],
                        "Measurement": ["Length", "Weight", "Capacity", "Time", "Money"]
                    }
                },
                "Class 5": {
                    "units": [
                        "Numbers and Operations",
                        "Fractions and Decimals", 
                        "Geometry",
                        "Measurement",
                        "Data Handling"
                    ],
                    "topics": {
                        "Numbers and Operations": ["Place Value", "Addition", "Subtraction", "Multiplication", "Division"],
                        "Fractions and Decimals": ["Fractions", "Decimals", "Addition/Subtraction of Fractions"],
                        "Geometry": ["Lines and Angles", "Triangles", "Quadrilaterals", "Circles"],
                        "Measurement": ["Length", "Weight", "Capacity", "Time", "Money"],
                        "Data Handling": ["Pictographs", "Bar Graphs", "Tables"]
                    }
                },
                "Class 6": {
                    "units": [
                        "Number System",
                        "Algebra",
                        "Geometry",
                        "Mensuration",
                        "Data Handling"
                    ],
                    "topics": {
                        "Number System": ["Natural Numbers", "Whole Numbers", "Integers", "Fractions", "Decimals"],
                        "Algebra": ["Variables", "Expressions", "Equations"],
                        "Geometry": ["Basic Geometrical Ideas", "Understanding Elementary Shapes"],
                        "Mensuration": ["Perimeter", "Area", "Volume"],
                        "Data Handling": ["Collection of Data", "Representation of Data"]
                    }
                },
                "Class 7": {
                    "units": [
                        "Number System",
                        "Algebra",
                        "Geometry",
                        "Mensuration",
                        "Data Handling"
                    ],
                    "topics": {
                        "Number System": ["Integers", "Fractions and Decimals", "Rational Numbers"],
                        "Algebra": ["Algebraic Expressions", "Linear Equations"],
                        "Geometry": ["Lines and Angles", "Triangles", "Congruence"],
                        "Mensuration": ["Perimeter and Area", "Volume and Surface Area"],
                        "Data Handling": ["Data Collection", "Data Representation", "Probability"]
                    }
                },
                "Class 8": {
                    "units": [
                        "Number System",
                        "Algebra",
                        "Geometry",
                        "Mensuration",
                        "Data Handling"
                    ],
                    "topics": {
                        "Number System": ["Rational Numbers", "Powers", "Square and Square Roots", "Cube and Cube Roots"],
                        "Algebra": ["Algebraic Expressions", "Linear Equations", "Factorisation"],
                        "Geometry": ["Understanding Quadrilaterals", "Practical Geometry", "Visualising Solid Shapes"],
                        "Mensuration": ["Area of Trapezium", "Surface Area and Volume"],
                        "Data Handling": ["Data Handling", "Graphs", "Probability"]
                    }
                },
                "Class 9": {
                    "units": [
                        "Number Systems",
                        "Algebra",
                        "Coordinate Geometry",
                        "Geometry",
                        "Mensuration",
                        "Statistics and Probability"
                    ],
                    "topics": {
                        "Number Systems": ["Real Numbers", "Irrational Numbers", "Rational Numbers"],
                        "Algebra": ["Polynomials", "Linear Equations in Two Variables", "Quadratic Equations"],
                        "Coordinate Geometry": ["Coordinate Geometry", "Distance Formula", "Section Formula"],
                        "Geometry": ["Lines and Angles", "Triangles", "Quadrilaterals", "Circles", "Constructions"],
                        "Mensuration": ["Areas of Parallelograms and Triangles", "Surface Areas and Volumes"],
                        "Statistics and Probability": ["Statistics", "Probability"]
                    }
                },
                "Class 10": {
                    "units": [
                        "Real Numbers",
                        "Polynomials",
                        "Pair of Linear Equations",
                        "Quadratic Equations",
                        "Arithmetic Progressions",
                        "Triangles",
                        "Coordinate Geometry",
                        "Introduction to Trigonometry",
                        "Applications of Trigonometry",
                        "Circles",
                        "Constructions",
                        "Areas Related to Circles",
                        "Surface Areas and Volumes",
                        "Statistics",
                        "Probability"
                    ],
                    "topics": {
                        "Real Numbers": ["Euclid's Division Lemma", "Fundamental Theorem of Arithmetic", "Irrational Numbers"],
                        "Polynomials": ["Polynomials", "Division Algorithm", "Relationship between Zeroes and Coefficients"],
                        "Pair of Linear Equations": ["Linear Equations in Two Variables", "Graphical Method", "Algebraic Methods"],
                        "Quadratic Equations": ["Quadratic Equations", "Solution by Factorization", "Solution by Completing Square"],
                        "Arithmetic Progressions": ["Arithmetic Progressions", "nth Term", "Sum of n Terms"],
                        "Triangles": ["Similarity of Triangles", "Pythagoras Theorem", "Basic Proportionality Theorem"],
                        "Coordinate Geometry": ["Distance Formula", "Section Formula", "Area of Triangle"],
                        "Introduction to Trigonometry": ["Trigonometric Ratios", "Trigonometric Identities", "Trigonometric Tables"],
                        "Applications of Trigonometry": ["Heights and Distances", "Applications in Real Life"],
                        "Circles": ["Tangent to a Circle", "Number of Tangents", "Properties of Tangents"],
                        "Constructions": ["Division of Line Segment", "Construction of Tangents", "Construction of Triangles"],
                        "Areas Related to Circles": ["Perimeter and Area of Circle", "Areas of Sector and Segment"],
                        "Surface Areas and Volumes": ["Surface Areas", "Volumes", "Combination of Solids"],
                        "Statistics": ["Mean", "Median", "Mode", "Cumulative Frequency"],
                        "Probability": ["Probability", "Theoretical Probability", "Experimental Probability"]
                    }
                },
                "Class 11": {
                    "units": [
                        "Sets and Functions",
                        "Algebra",
                        "Coordinate Geometry",
                        "Calculus",
                        "Mathematical Reasoning",
                        "Statistics and Probability"
                    ],
                    "topics": {
                        "Sets and Functions": ["Sets", "Relations and Functions", "Trigonometric Functions"],
                        "Algebra": ["Complex Numbers", "Linear Inequalities", "Permutations and Combinations", "Binomial Theorem", "Sequences and Series"],
                        "Coordinate Geometry": ["Straight Lines", "Conic Sections", "Introduction to Three Dimensional Geometry"],
                        "Calculus": ["Limits and Derivatives", "Mathematical Reasoning"],
                        "Mathematical Reasoning": ["Mathematical Reasoning", "Statistics", "Probability"],
                        "Statistics and Probability": ["Statistics", "Probability"]
                    }
                },
                "Class 12": {
                    "units": [
                        "Relations and Functions",
                        "Algebra",
                        "Calculus",
                        "Vectors and Three-Dimensional Geometry",
                        "Linear Programming",
                        "Probability"
                    ],
                    "topics": {
                        "Relations and Functions": ["Relations and Functions", "Inverse Trigonometric Functions"],
                        "Algebra": ["Matrices", "Determinants"],
                        "Calculus": ["Continuity and Differentiability", "Applications of Derivatives", "Integrals", "Applications of Integrals", "Differential Equations"],
                        "Vectors and Three-Dimensional Geometry": ["Vectors", "Three-Dimensional Geometry"],
                        "Linear Programming": ["Linear Programming"],
                        "Probability": ["Probability"]
                    }
                }
            },
            "Science": {
                "Class 1": {
                    "units": ["Living World", "Materials", "Energy", "Earth and Space"],
                    "topics": {
                        "Living World": ["Plants Around Us", "Animals Around Us", "Parts of Plants", "Parts of Animals"],
                        "Materials": ["Objects Around Us", "Properties of Objects", "Uses of Materials"],
                        "Energy": ["Light and Sound", "Heat and Cold", "Simple Machines"],
                        "Earth and Space": ["Sun, Moon and Stars", "Weather", "Seasons"]
                    }
                },
                "Class 2": {
                    "units": ["Living World", "Materials", "Energy", "Earth and Space"],
                    "topics": {
                        "Living World": ["Plants", "Animals", "Human Body", "Food and Health"],
                        "Materials": ["Properties of Materials", "Uses of Materials", "Changes in Materials"],
                        "Energy": ["Light and Sound", "Heat and Cold", "Simple Machines"],
                        "Earth and Space": ["Sun, Moon and Stars", "Weather", "Seasons", "Natural Resources"]
                    }
                },
                "Class 3": {
                    "units": ["Living World", "Materials", "Energy", "Earth and Space"],
                    "topics": {
                        "Living World": ["Plants", "Animals", "Human Body", "Food and Health", "Habitats"],
                        "Materials": ["Properties of Materials", "Uses of Materials", "Changes in Materials"],
                        "Energy": ["Light and Sound", "Heat and Cold", "Simple Machines", "Electricity"],
                        "Earth and Space": ["Sun, Moon and Stars", "Weather", "Seasons", "Natural Resources"]
                    }
                },
                "Class 4": {
                    "units": ["Living World", "Materials", "Energy", "Earth and Space"],
                    "topics": {
                        "Living World": ["Plants", "Animals", "Human Body", "Food and Health", "Habitats", "Adaptations"],
                        "Materials": ["Properties of Materials", "Uses of Materials", "Changes in Materials", "States of Matter"],
                        "Energy": ["Light and Sound", "Heat and Cold", "Simple Machines", "Electricity", "Energy Conservation"],
                        "Earth and Space": ["Sun, Moon and Stars", "Weather", "Seasons", "Natural Resources", "Solar System"]
                    }
                },
                "Class 5": {
                    "units": [
                        "Living World",
                        "Materials",
                        "Energy",
                        "Earth and Space"
                    ],
                    "topics": {
                        "Living World": ["Plants", "Animals", "Human Body"],
                        "Materials": ["States of Matter", "Properties of Materials"],
                        "Energy": ["Forms of Energy", "Energy Conservation"],
                        "Earth and Space": ["Solar System", "Weather", "Natural Resources"]
                    }
                },
                "Class 6": {
                    "units": [
                        "Physics",
                        "Chemistry", 
                        "Biology"
                    ],
                    "topics": {
                        "Physics": ["Motion and Measurement", "Light", "Electricity", "Magnets"],
                        "Chemistry": ["Separation of Substances", "Changes Around Us", "Air Around Us"],
                        "Biology": ["Food", "Living Organisms", "Plants", "Body Movements"]
                    }
                },
                "Class 7": {
                    "units": [
                        "Physics",
                        "Chemistry",
                        "Biology"
                    ],
                    "topics": {
                        "Physics": ["Heat", "Acids, Bases and Salts", "Physical and Chemical Changes", "Weather, Climate and Adaptations"],
                        "Chemistry": ["Fibre to Fabric", "Acids, Bases and Salts", "Physical and Chemical Changes"],
                        "Biology": ["Nutrition in Plants", "Nutrition in Animals", "Respiration in Organisms", "Transportation in Animals and Plants"]
                    }
                },
                "Class 8": {
                    "units": [
                        "Physics",
                        "Chemistry",
                        "Biology"
                    ],
                    "topics": {
                        "Physics": ["Force and Pressure", "Friction", "Sound", "Light", "Chemical Effects of Electric Current"],
                        "Chemistry": ["Synthetic Fibres and Plastics", "Materials: Metals and Non-metals", "Coal and Petroleum", "Combustion and Flame"],
                        "Biology": ["Crop Production and Management", "Microorganisms", "Conservation of Plants and Animals", "Cell Structure and Functions"]
                    }
                },
                "Class 9": {
                    "units": [
                        "Physics",
                        "Chemistry",
                        "Biology"
                    ],
                    "topics": {
                        "Physics": ["Motion", "Force and Laws of Motion", "Gravitation", "Work and Energy", "Sound"],
                        "Chemistry": ["Matter in Our Surroundings", "Is Matter Around Us Pure", "Atoms and Molecules", "Structure of the Atom"],
                        "Biology": ["The Fundamental Unit of Life", "Tissues", "Diversity in Living Organisms", "Why Do We Fall Ill", "Natural Resources"]
                    }
                },
                "Class 10": {
                    "units": [
                        "Physics",
                        "Chemistry",
                        "Biology"
                    ],
                    "topics": {
                        "Physics": ["Light - Reflection and Refraction", "Human Eye and Colourful World", "Electricity", "Magnetic Effects of Electric Current", "Sources of Energy"],
                        "Chemistry": ["Chemical Reactions and Equations", "Acids, Bases and Salts", "Metals and Non-metals", "Carbon and its Compounds", "Periodic Classification of Elements"],
                        "Biology": ["Life Processes", "Control and Coordination", "How do Organisms Reproduce", "Heredity and Evolution", "Our Environment", "Management of Natural Resources"]
                    }
                },
                "Class 11": {
                    "units": [
                        "Physics",
                        "Chemistry",
                        "Biology"
                    ],
                    "topics": {
                        "Physics": ["Physical World", "Units and Measurements", "Motion in a Straight Line", "Motion in a Plane", "Laws of Motion", "Work, Energy and Power", "System of Particles and Rotational Motion", "Gravitation", "Mechanical Properties of Solids", "Mechanical Properties of Fluids", "Thermal Properties of Matter", "Thermodynamics", "Kinetic Theory", "Oscillations", "Waves"],
                        "Chemistry": ["Some Basic Concepts of Chemistry", "Structure of Atom", "Classification of Elements and Periodicity in Properties", "Chemical Bonding and Molecular Structure", "States of Matter", "Thermodynamics", "Equilibrium", "Redox Reactions", "Hydrogen", "The s-Block Elements", "The p-Block Elements", "Organic Chemistry", "Hydrocarbons", "Environmental Chemistry"],
                        "Biology": ["The Living World", "Biological Classification", "Plant Kingdom", "Animal Kingdom", "Morphology of Flowering Plants", "Anatomy of Flowering Plants", "Structural Organisation in Animals", "Cell: The Unit of Life", "Biomolecules", "Cell Cycle and Cell Division", "Transport in Plants", "Mineral Nutrition", "Photosynthesis in Higher Plants", "Respiration in Plants", "Plant Growth and Development", "Digestion and Absorption", "Breathing and Exchange of Gases", "Body Fluids and Circulation", "Excretory Products and their Elimination", "Locomotion and Movement", "Neural Control and Coordination", "Chemical Coordination and Integration"]
                    }
                },
                "Class 12": {
                    "units": [
                        "Physics",
                        "Chemistry",
                        "Biology"
                    ],
                    "topics": {
                        "Physics": ["Electric Charges and Fields", "Electrostatic Potential and Capacitance", "Current Electricity", "Moving Charges and Magnetism", "Magnetism and Matter", "Electromagnetic Induction", "Alternating Current", "Electromagnetic Waves", "Ray Optics and Optical Instruments", "Wave Optics", "Dual Nature of Radiation and Matter", "Atoms", "Nuclei", "Semiconductor Electronics", "Communication Systems"],
                        "Chemistry": ["The Solid State", "Solutions", "Electrochemistry", "Chemical Kinetics", "Surface Chemistry", "General Principles and Processes of Isolation of Elements", "The p-Block Elements", "The d and f Block Elements", "Coordination Compounds", "Haloalkanes and Haloarenes", "Alcohols, Phenols and Ethers", "Aldehydes, Ketones and Carboxylic Acids", "Amines", "Biomolecules", "Polymers", "Chemistry in Everyday Life"],
                        "Biology": ["Reproduction in Organisms", "Sexual Reproduction in Flowering Plants", "Human Reproduction", "Reproductive Health", "Principles of Inheritance and Variation", "Molecular Basis of Inheritance", "Evolution", "Human Health and Disease", "Strategies for Enhancement in Food Production", "Microbes in Human Welfare", "Biotechnology: Principles and Processes", "Biotechnology and its Applications", "Organisms and Populations", "Ecosystem", "Biodiversity and Conservation", "Environmental Issues"]
                    }
                }
            },
            "English": {
                "Class 5": {
                    "units": [
                        "Reading",
                        "Writing",
                        "Grammar",
                        "Literature"
                    ],
                    "topics": {
                        "Reading": ["Comprehension", "Vocabulary", "Reading Skills"],
                        "Writing": ["Paragraph Writing", "Letter Writing", "Story Writing"],
                        "Grammar": ["Parts of Speech", "Tenses", "Articles", "Prepositions"],
                        "Literature": ["Poems", "Stories", "Prose"]
                    }
                },
                "Class 6": {
                    "units": [
                        "Reading",
                        "Writing", 
                        "Grammar",
                        "Literature"
                    ],
                    "topics": {
                        "Reading": ["Reading Comprehension", "Vocabulary Building", "Reading Strategies"],
                        "Writing": ["Essay Writing", "Letter Writing", "Creative Writing"],
                        "Grammar": ["Nouns", "Pronouns", "Verbs", "Adjectives", "Adverbs"],
                        "Literature": ["Poetry", "Short Stories", "Novels"]
                    }
                },
                "Class 7": {
                    "units": [
                        "Reading",
                        "Writing",
                        "Grammar", 
                        "Literature"
                    ],
                    "topics": {
                        "Reading": ["Comprehension Skills", "Critical Reading", "Vocabulary Enhancement"],
                        "Writing": ["Descriptive Writing", "Narrative Writing", "Formal Letters"],
                        "Grammar": ["Tenses", "Voice", "Narration", "Modals"],
                        "Literature": ["Poetry Analysis", "Prose", "Drama"]
                    }
                },
                "Class 8": {
                    "units": [
                        "Reading",
                        "Writing",
                        "Grammar",
                        "Literature"
                    ],
                    "topics": {
                        "Reading": ["Advanced Comprehension", "Critical Analysis", "Vocabulary"],
                        "Writing": ["Essay Writing", "Report Writing", "Creative Writing"],
                        "Grammar": ["Advanced Tenses", "Conditionals", "Reported Speech", "Active-Passive Voice"],
                        "Literature": ["Poetry", "Prose", "Drama", "Novels"]
                    }
                }
            },
            "Social Studies": {
                "Class 5": {
                    "units": [
                        "History",
                        "Geography",
                        "Civics"
                    ],
                    "topics": {
                        "History": ["Ancient Civilizations", "Freedom Struggle", "Indian Culture"],
                        "Geography": ["Maps", "Physical Features", "Climate", "Natural Resources"],
                        "Civics": ["Democracy", "Rights and Duties", "Government"]
                    }
                },
                "Class 6": {
                    "units": [
                        "History",
                        "Geography",
                        "Civics"
                    ],
                    "topics": {
                        "History": ["Ancient India", "Medieval India", "Modern India"],
                        "Geography": ["The Earth", "Globe", "Maps", "Major Domains"],
                        "Civics": ["Diversity", "Government", "Local Government"]
                    }
                },
                "Class 7": {
                    "units": [
                        "History",
                        "Geography",
                        "Civics"
                    ],
                    "topics": {
                        "History": ["Medieval India", "Mughal Empire", "British Rule"],
                        "Geography": ["Environment", "Inside Our Earth", "Our Changing Earth"],
                        "Civics": ["Equality", "State Government", "Media"]
                    }
                },
                "Class 8": {
                    "units": [
                        "History",
                        "Geography",
                        "Civics"
                    ],
                    "topics": {
                        "History": ["Modern India", "Freedom Movement", "Independence"],
                        "Geography": ["Resources", "Agriculture", "Industries", "Human Resources"],
                        "Civics": ["Constitution", "Parliamentary Democracy", "Judiciary"]
                    }
                }
            }
        }

        # ICSE Syllabus Structure (similar but with some differences)
        self.icse_syllabus = {
            "Mathematics": {
                "Class 5": {
                    "units": [
                        "Numbers",
                        "Fractions and Decimals",
                        "Geometry",
                        "Measurement",
                        "Data Handling"
                    ],
                    "topics": {
                        "Numbers": ["Place Value", "Operations", "Factors and Multiples"],
                        "Fractions and Decimals": ["Fractions", "Decimals", "Operations"],
                        "Geometry": ["Lines", "Angles", "Shapes", "Symmetry"],
                        "Measurement": ["Length", "Weight", "Capacity", "Time"],
                        "Data Handling": ["Pictographs", "Bar Charts", "Tables"]
                    }
                },
                "Class 6": {
                    "units": [
                        "Number System",
                        "Algebra",
                        "Geometry",
                        "Mensuration",
                        "Statistics"
                    ],
                    "topics": {
                        "Number System": ["Natural Numbers", "Integers", "Fractions", "Decimals"],
                        "Algebra": ["Variables", "Expressions", "Simple Equations"],
                        "Geometry": ["Basic Geometry", "Angles", "Triangles"],
                        "Mensuration": ["Perimeter", "Area", "Volume"],
                        "Statistics": ["Data Collection", "Representation"]
                    }
                },
                "Class 7": {
                    "units": [
                        "Number System",
                        "Algebra",
                        "Geometry",
                        "Mensuration",
                        "Statistics"
                    ],
                    "topics": {
                        "Number System": ["Integers", "Fractions", "Decimals", "Rational Numbers"],
                        "Algebra": ["Algebraic Expressions", "Linear Equations"],
                        "Geometry": ["Lines and Angles", "Triangles", "Congruence"],
                        "Mensuration": ["Perimeter and Area", "Volume"],
                        "Statistics": ["Data Handling", "Probability"]
                    }
                },
                "Class 8": {
                    "units": [
                        "Number System",
                        "Algebra",
                        "Geometry",
                        "Mensuration",
                        "Statistics"
                    ],
                    "topics": {
                        "Number System": ["Rational Numbers", "Powers", "Square Roots", "Cube Roots"],
                        "Algebra": ["Algebraic Expressions", "Linear Equations", "Factorisation"],
                        "Geometry": ["Quadrilaterals", "Practical Geometry", "Solid Shapes"],
                        "Mensuration": ["Area", "Surface Area", "Volume"],
                        "Statistics": ["Data Handling", "Graphs", "Probability"]
                    }
                }
            }
        }

        # Question Paper Templates
        self.question_templates = {
            "Mathematics": {
                "MCQ": [
                    "What is the value of {expression}?",
                    "Which of the following is {condition}?",
                    "If {given}, then {find} equals:",
                    "The {concept} of {number} is:",
                    "Which number comes next in the pattern: {pattern}?"
                ],
                "Short Answer": [
                    "Solve: {problem}",
                    "Find the {concept} of {numbers}",
                    "Calculate: {expression}",
                    "Simplify: {expression}",
                    "Evaluate: {expression}"
                ],
                "Long Answer": [
                    "Solve the following step by step: {complex_problem}",
                    "Prove that: {theorem}",
                    "Find the solution and verify: {problem}",
                    "Solve using {method}: {problem}",
                    "Work out the complete solution: {problem}"
                ]
            },
            "Science": {
                "MCQ": [
                    "Which of the following is {concept}?",
                    "What happens when {action}?",
                    "The function of {organ/system} is:",
                    "Which process is responsible for {phenomenon}?",
                    "The correct sequence of {process} is:"
                ],
                "Short Answer": [
                    "Define {concept}",
                    "Explain {phenomenon}",
                    "What is the role of {component}?",
                    "Describe {process}",
                    "State the importance of {concept}"
                ],
                "Long Answer": [
                    "Explain in detail: {topic}",
                    "Describe the process of {process} with diagram",
                    "Compare and contrast {concept1} and {concept2}",
                    "Explain the working of {system}",
                    "Discuss the importance of {concept} in daily life"
                ]
            },
            "English": {
                "MCQ": [
                    "Choose the correct form of the verb: {sentence}",
                    "Select the appropriate word: {context}",
                    "Which word means the same as {word}?",
                    "Choose the correct tense: {sentence}",
                    "Select the right preposition: {sentence}"
                ],
                "Short Answer": [
                    "Write a paragraph on {topic}",
                    "Change the voice: {sentence}",
                    "Transform the sentence: {sentence}",
                    "Write a letter to {recipient} about {topic}",
                    "Complete the story: {beginning}"
                ],
                "Long Answer": [
                    "Write an essay on {topic}",
                    "Analyze the poem: {poem_title}",
                    "Write a story based on {theme}",
                    "Describe {person/place/event} in detail",
                    "Write a report on {event/topic}"
                ]
            }
        }

    def get_syllabus(self, board: str, subject: str, class_level: str) -> Dict[str, Any]:
        """Get syllabus for specific board, subject and class"""
        if board.upper() == "CBSE":
            return self.cbse_syllabus.get(subject, {}).get(class_level, {})
        elif board.upper() == "ICSE":
            return self.icse_syllabus.get(subject, {}).get(class_level, {})
        return {}

    def generate_question_paper(self, board: str, subject: str, class_level: str, 
                              exam_type: str = "Unit Test", duration: int = 60, 
                              selected_topics: List[str] = None) -> Dict[str, Any]:
        """Generate a complete question paper based on selected topics"""
        
        syllabus = self.get_syllabus(board, subject, class_level)
        if not syllabus:
            return {"error": "Syllabus not found for the given parameters"}

        # If no topics selected, use all topics from syllabus
        if not selected_topics:
            selected_topics = []
            for unit, topics in syllabus.get("topics", {}).items():
                selected_topics.extend(topics)

        # Paper structure based on board and class
        if board.upper() == "CBSE":
            paper_structure = self._get_cbse_paper_structure(class_level, subject)
        else:
            paper_structure = self._get_icse_paper_structure(class_level, subject)

        # Generate questions for each section based on selected topics
        sections = []
        total_marks = 0
        
        for section in paper_structure:
            section_questions = []
            section_marks = 0
            
            for question_type in section["question_types"]:
                num_questions = question_type["count"]
                marks_per_question = question_type["marks"]
                
                for i in range(num_questions):
                    question = self._generate_question_for_topics(subject, question_type["type"], 
                                                               selected_topics, class_level)
                    section_questions.append({
                        "question_number": len(section_questions) + 1,
                        "question": question["question"],
                        "marks": marks_per_question,
                        "type": question_type["type"],
                        "topic": question["topic"]
                    })
                    section_marks += marks_per_question
            
            sections.append({
                "section_name": section["name"],
                "section_marks": section_marks,
                "questions": section_questions
            })
            total_marks += section_marks

        return {
            "board": board,
            "subject": subject,
            "class": class_level,
            "exam_type": exam_type,
            "duration": duration,
            "total_marks": total_marks,
            "selected_topics": selected_topics,
            "instructions": self._get_paper_instructions(board, subject, class_level),
            "sections": sections
        }

    def _get_cbse_paper_structure(self, class_level: str, subject: str) -> List[Dict]:
        """Get CBSE paper structure"""
        if subject == "Mathematics":
            if class_level in ["Class 5", "Class 6"]:
                return [
                    {
                        "name": "Section A",
                        "question_types": [
                            {"type": "MCQ", "count": 10, "marks": 1},
                            {"type": "Short Answer", "count": 5, "marks": 2}
                        ]
                    },
                    {
                        "name": "Section B", 
                        "question_types": [
                            {"type": "Short Answer", "count": 5, "marks": 3}
                        ]
                    },
                    {
                        "name": "Section C",
                        "question_types": [
                            {"type": "Long Answer", "count": 3, "marks": 5}
                        ]
                    }
                ]
            else:  # Class 7, 8
                return [
                    {
                        "name": "Section A",
                        "question_types": [
                            {"type": "MCQ", "count": 15, "marks": 1},
                            {"type": "Short Answer", "count": 5, "marks": 2}
                        ]
                    },
                    {
                        "name": "Section B",
                        "question_types": [
                            {"type": "Short Answer", "count": 5, "marks": 3}
                        ]
                    },
                    {
                        "name": "Section C",
                        "question_types": [
                            {"type": "Long Answer", "count": 4, "marks": 5}
                        ]
                    }
                ]
        else:
            # Default structure for other subjects
            return [
                {
                    "name": "Section A",
                    "question_types": [
                        {"type": "MCQ", "count": 10, "marks": 1},
                        {"type": "Short Answer", "count": 5, "marks": 2}
                    ]
                },
                {
                    "name": "Section B",
                    "question_types": [
                        {"type": "Short Answer", "count": 5, "marks": 3},
                        {"type": "Long Answer", "count": 3, "marks": 5}
                    ]
                }
            ]

    def _get_icse_paper_structure(self, class_level: str, subject: str) -> List[Dict]:
        """Get ICSE paper structure"""
        # Similar to CBSE but with slight variations
        return self._get_cbse_paper_structure(class_level, subject)

    def _generate_question_for_topics(self, subject: str, question_type: str, 
                                    selected_topics: List[str], class_level: str) -> Dict[str, str]:
        """Generate a specific question for selected topics"""
        
        if not selected_topics:
            return {"question": "Sample question", "topic": "General"}
        
        # Select a random topic from the selected topics
        topic = random.choice(selected_topics)
        
        # Get question template
        templates = self.question_templates.get(subject, {}).get(question_type, [])
        if not templates:
            return {"question": f"Explain {topic} in detail.", "topic": topic}
        
        template = random.choice(templates)
        
        # Fill template with content
        if subject == "Mathematics":
            question_text = self._fill_math_template_for_topic(template, topic, class_level)
        elif subject == "Science":
            question_text = self._fill_science_template_for_topic(template, topic)
        elif subject == "English":
            question_text = self._fill_english_template_for_topic(template, topic)
        else:
            question_text = template.format(topic=topic)
        
        return {"question": question_text, "topic": topic}

    def _generate_question(self, subject: str, question_type: str, 
                          syllabus: Dict, class_level: str) -> str:
        """Generate a specific question"""
        
        # Get random unit and topic
        units = list(syllabus.get("units", []))
        if not units:
            return "Sample question for the topic"
        
        unit = random.choice(units)
        topics = syllabus.get("topics", {}).get(unit, [])
        topic = random.choice(topics) if topics else unit
        
        # Get question template
        templates = self.question_templates.get(subject, {}).get(question_type, [])
        if not templates:
            return f"Explain {topic} in detail."
        
        template = random.choice(templates)
        
        # Fill template with content
        if subject == "Mathematics":
            return self._fill_math_template(template, topic, class_level)
        elif subject == "Science":
            return self._fill_science_template(template, topic, unit)
        elif subject == "English":
            return self._fill_english_template(template, topic)
        else:
            return template.format(topic=topic)

    def _fill_math_template_for_topic(self, template: str, topic: str, class_level: str) -> str:
        """Fill mathematics question template for specific topics"""
        
        # Topic-specific problems and expressions
        topic_specific_content = {
            "Addition": {
                "Class 5": ["25 + 15", "100 + 45", "250 + 75"],
                "Class 6": ["(-5) + 8", "3/4 + 1/2", "2.5 + 3.7"],
                "Class 7": ["(-12) + (-8)", "3/4 + 2/3", "0.25 + 0.75"],
                "Class 8": ["(-15) + (-3)", "2/3 + 1/4", "√25 + √9"]
            },
            "Subtraction": {
                "Class 5": ["100 - 45", "250 - 75", "500 - 125"],
                "Class 6": ["8 - (-5)", "1/2 - 1/4", "3.7 - 2.5"],
                "Class 7": ["(-8) - (-12)", "2/3 - 1/4", "0.75 - 0.25"],
                "Class 8": ["(-3) - (-15)", "1/4 - 2/3", "√16 - √9"]
            },
            "Multiplication": {
                "Class 5": ["12 × 8", "15 × 6", "25 × 4"],
                "Class 6": ["2.5 × 3", "3/4 × 2", "0.5 × 8"],
                "Class 7": ["3/4 × 2/3", "0.25 × 4", "(-2) × 3"],
                "Class 8": ["(-15) × (-3)", "2/3 × 1/4", "√4 × √9"]
            },
            "Division": {
                "Class 5": ["96 ÷ 6", "120 ÷ 8", "200 ÷ 5"],
                "Class 6": ["15 ÷ 0.5", "3/4 ÷ 2", "8 ÷ 0.25"],
                "Class 7": ["1 ÷ 2/3", "0.25 ÷ 0.5", "(-12) ÷ 3"],
                "Class 8": ["2/3 ÷ 1/4", "√16 ÷ √4", "(-15) ÷ (-3)"]
            },
            "Fractions": {
                "Class 5": ["3/4 + 1/2", "2/3 - 1/6", "1/2 × 3/4"],
                "Class 6": ["3/4 + 1/2", "2/3 - 1/4", "3/4 × 2/3"],
                "Class 7": ["3/4 + 2/3", "2/3 - 1/4", "3/4 × 2/3"],
                "Class 8": ["2/3 + 1/4", "1/4 - 2/3", "2/3 × 1/4"]
            },
            "Decimals": {
                "Class 5": ["2.5 + 3.7", "5.8 - 2.3", "1.5 × 4"],
                "Class 6": ["2.5 + 3.7", "5.8 - 2.3", "2.5 × 3"],
                "Class 7": ["0.25 + 0.75", "1.5 - 0.8", "0.25 × 4"],
                "Class 8": ["3.14 + 2.86", "5.5 - 2.7", "2.5 × 0.4"]
            },
            "Algebraic Expressions": {
                "Class 6": ["2x + 3", "3y - 5", "4z + 2"],
                "Class 7": ["2x + 3y", "3x - 2y", "4x + 5"],
                "Class 8": ["x² + 3x + 2", "2x² - 5x + 3", "3x + 2y - z"]
            },
            "Linear Equations": {
                "Class 6": ["x + 5 = 12", "2x - 3 = 7", "3x + 2 = 11"],
                "Class 7": ["2x + 5 = 13", "3x - 4 = 8", "5x + 3 = 18"],
                "Class 8": ["3x + 2 = 11", "2x - 5 = 7", "4x + 3 = 19"]
            },
            "Geometry": {
                "Class 5": ["Find the perimeter of a rectangle with length 8cm and breadth 6cm", "Calculate the area of a square with side 5cm"],
                "Class 6": ["Find the area of a triangle with base 6cm and height 4cm", "Calculate the perimeter of a circle with radius 3cm"],
                "Class 7": ["Find the area of a trapezium with parallel sides 8cm and 6cm, height 4cm", "Calculate the volume of a cube with side 3cm"],
                "Class 8": ["Find the surface area of a cylinder with radius 2cm and height 5cm", "Calculate the volume of a sphere with radius 3cm"]
            }
        }
        
        if "expression" in template:
            # Find matching topic
            for topic_key, content in topic_specific_content.items():
                if topic_key.lower() in topic.lower():
                    expressions = content.get(class_level, ["25 + 15"])
                    expression = random.choice(expressions)
                    return template.format(expression=expression)
            
            # Default expressions if topic not found
            expressions = {
                "Class 5": ["25 + 15", "100 - 45", "12 × 8", "96 ÷ 6"],
                "Class 6": ["(-5) + 8", "3/4 + 1/2", "2.5 × 3", "15 ÷ 0.5"],
                "Class 7": ["(-12) + (-8)", "3/4 × 2/3", "0.25 × 4", "√16"],
                "Class 8": ["(-15) × (-3)", "2/3 ÷ 1/4", "√25 + √9", "2³ × 3²"]
            }
            expression = random.choice(expressions.get(class_level, ["25 + 15"]))
            return template.format(expression=expression)
        
        elif "problem" in template:
            # Find matching topic
            for topic_key, content in topic_specific_content.items():
                if topic_key.lower() in topic.lower():
                    problems = content.get(class_level, ["25 + 15"])
                    problem = random.choice(problems)
                    return template.format(problem=problem)
            
            # Default problems if topic not found
            problems = {
                "Class 5": ["25 + 15 × 2", "Find the perimeter of a rectangle with length 8cm and breadth 6cm"],
                "Class 6": ["(-5) + 8 - 3", "Simplify: 3/4 + 1/2 - 1/4"],
                "Class 7": ["(-12) + (-8) × 2", "Solve: 2x + 5 = 13"],
                "Class 8": ["(-15) × (-3) + 10", "Factorize: x² + 5x + 6"]
            }
            problem = random.choice(problems.get(class_level, ["25 + 15"]))
            return template.format(problem=problem)
        
        else:
            return template.format(topic=topic)

    def _fill_math_template(self, template: str, topic: str, class_level: str) -> str:
        """Fill mathematics question template"""
        if "expression" in template:
            expressions = {
                "Class 5": ["25 + 15", "100 - 45", "12 × 8", "96 ÷ 6"],
                "Class 6": ["(-5) + 8", "3/4 + 1/2", "2.5 × 3", "15 ÷ 0.5"],
                "Class 7": ["(-12) + (-8)", "3/4 × 2/3", "0.25 × 4", "√16"],
                "Class 8": ["(-15) × (-3)", "2/3 ÷ 1/4", "√25 + √9", "2³ × 3²"]
            }
            expression = random.choice(expressions.get(class_level, ["25 + 15"]))
            return template.format(expression=expression)
        
        elif "problem" in template:
            problems = {
                "Class 5": ["25 + 15 × 2", "Find the perimeter of a rectangle with length 8cm and breadth 6cm"],
                "Class 6": ["(-5) + 8 - 3", "Simplify: 3/4 + 1/2 - 1/4"],
                "Class 7": ["(-12) + (-8) × 2", "Solve: 2x + 5 = 13"],
                "Class 8": ["(-15) × (-3) + 10", "Factorize: x² + 5x + 6"]
            }
            problem = random.choice(problems.get(class_level, ["25 + 15"]))
            return template.format(problem=problem)
        
        else:
            return template.format(topic=topic)

    def _fill_science_template_for_topic(self, template: str, topic: str) -> str:
        """Fill science question template for specific topics"""
        
        # Topic-specific science content
        topic_specific_content = {
            "Photosynthesis": {
                "concepts": ["chlorophyll", "sunlight", "carbon dioxide", "oxygen", "glucose"],
                "phenomena": ["light energy conversion", "chemical energy storage", "gas exchange"],
                "processes": ["light-dependent reactions", "Calvin cycle", "stomatal opening"]
            },
            "Respiration": {
                "concepts": ["oxygen", "carbon dioxide", "energy", "mitochondria", "ATP"],
                "phenomena": ["gas exchange", "energy release", "cellular respiration"],
                "processes": ["glycolysis", "Krebs cycle", "electron transport chain"]
            },
            "Digestion": {
                "concepts": ["enzymes", "nutrients", "absorption", "stomach", "intestines"],
                "phenomena": ["chemical breakdown", "nutrient absorption", "waste elimination"],
                "processes": ["mechanical digestion", "chemical digestion", "absorption"]
            },
            "Light": {
                "concepts": ["reflection", "refraction", "dispersion", "wavelength", "frequency"],
                "phenomena": ["light reflection", "light refraction", "color formation"],
                "processes": ["light absorption", "light transmission", "light scattering"]
            },
            "Sound": {
                "concepts": ["vibration", "frequency", "amplitude", "wavelength", "echo"],
                "phenomena": ["sound propagation", "echo formation", "resonance"],
                "processes": ["sound production", "sound transmission", "sound reception"]
            },
            "Heat": {
                "concepts": ["temperature", "thermal energy", "conduction", "convection", "radiation"],
                "phenomena": ["heat transfer", "thermal expansion", "phase changes"],
                "processes": ["heat conduction", "heat convection", "heat radiation"]
            },
            "Chemical Reactions": {
                "concepts": ["reactants", "products", "catalyst", "energy", "equilibrium"],
                "phenomena": ["chemical reactions", "energy changes", "color changes"],
                "processes": ["synthesis", "decomposition", "displacement"]
            }
        }
        
        if "concept" in template:
            # Find matching topic
            for topic_key, content in topic_specific_content.items():
                if topic_key.lower() in topic.lower():
                    concept = random.choice(content["concepts"])
                    return template.format(concept=concept)
            return template.format(concept=topic)
        
        elif "phenomenon" in template:
            # Find matching topic
            for topic_key, content in topic_specific_content.items():
                if topic_key.lower() in topic.lower():
                    phenomenon = random.choice(content["phenomena"])
                    return template.format(phenomenon=phenomenon)
            
            # Default phenomena
            phenomena = ["light reflection", "sound propagation", "heat transfer", "chemical reactions"]
            phenomenon = random.choice(phenomena)
            return template.format(phenomenon=phenomenon)
        
        else:
            return template.format(topic=topic)

    def _fill_science_template(self, template: str, topic: str, unit: str) -> str:
        """Fill science question template"""
        if "concept" in template:
            return template.format(concept=topic)
        elif "phenomenon" in template:
            phenomena = {
                "Physics": ["light reflection", "sound propagation", "heat transfer"],
                "Chemistry": ["chemical reactions", "state changes", "dissolution"],
                "Biology": ["photosynthesis", "respiration", "digestion"]
            }
            phenomenon = random.choice(phenomena.get(unit, [topic]))
            return template.format(phenomenon=phenomenon)
        else:
            return template.format(topic=topic)

    def _fill_english_template_for_topic(self, template: str, topic: str) -> str:
        """Fill English question template for specific topics"""
        
        # Topic-specific English content
        topic_specific_content = {
            "Grammar": {
                "sentences": [
                    "The students _____ to school every day. (go/goes/going)",
                    "She _____ a beautiful song yesterday. (sing/sang/sung)",
                    "The book _____ on the table. (is/are/were)",
                    "They _____ playing in the garden. (is/are/were)",
                    "He _____ his homework last night. (do/did/done)"
                ],
                "topics": ["parts of speech", "tenses", "articles", "prepositions", "conjunctions"]
            },
            "Vocabulary": {
                "sentences": [
                    "The _____ of the mountain was breathtaking. (scene/scenery/scenic)",
                    "She showed great _____ in solving the problem. (patience/patient/patiently)",
                    "The _____ of the story was very interesting. (plot/plotted/plotting)"
                ],
                "topics": ["word meanings", "synonyms", "antonyms", "homophones", "idioms"]
            },
            "Reading Comprehension": {
                "sentences": [
                    "Read the following passage and answer the questions below.",
                    "Based on the text, what can you infer about the main character?",
                    "What is the main idea of the passage?"
                ],
                "topics": ["main idea", "supporting details", "inference", "context clues", "author's purpose"]
            },
            "Writing": {
                "sentences": [
                    "Write a paragraph about your favorite hobby.",
                    "Describe a memorable event from your life.",
                    "Write a letter to your friend about your summer vacation."
                ],
                "topics": ["paragraph writing", "essay writing", "letter writing", "story writing", "descriptive writing"]
            }
        }
        
        if "sentence" in template:
            # Find matching topic
            for topic_key, content in topic_specific_content.items():
                if topic_key.lower() in topic.lower():
                    sentence = random.choice(content["sentences"])
                    return template.format(sentence=sentence)
            
            # Default sentences
            sentences = [
                "The students _____ to school every day. (go/goes/going)",
                "She _____ a beautiful song yesterday. (sing/sang/sung)",
                "The book _____ on the table. (is/are/were)"
            ]
            sentence = random.choice(sentences)
            return template.format(sentence=sentence)
        
        else:
            return template.format(topic=topic)

    def _fill_english_template(self, template: str, topic: str) -> str:
        """Fill English question template"""
        if "sentence" in template:
            sentences = [
                "The students _____ to school every day. (go/goes/going)",
                "She _____ a beautiful song yesterday. (sing/sang/sung)",
                "The book _____ on the table. (is/are/were)"
            ]
            sentence = random.choice(sentences)
            return template.format(sentence=sentence)
        else:
            return template.format(topic=topic)

    def _get_paper_instructions(self, board: str, subject: str, class_level: str) -> List[str]:
        """Get paper instructions"""
        instructions = [
            "All questions are compulsory.",
            "Write your answers neatly and clearly.",
            "Show all your working for mathematical problems.",
            "Draw diagrams wherever necessary."
        ]
        
        if board.upper() == "CBSE":
            instructions.extend([
                "Follow CBSE marking scheme.",
                "Use blue or black pen only."
            ])
        else:
            instructions.extend([
                "Follow ICSE marking scheme.",
                "Use blue or black pen only."
            ])
        
        return instructions

    def get_lesson_plan_template(self, board: str, subject: str, class_level: str, 
                                topic: str) -> Dict[str, Any]:
        """Generate lesson plan template for specific board and topic"""
        
        syllabus = self.get_syllabus(board, subject, class_level)
        if not syllabus:
            return {"error": "Syllabus not found"}

        # Find the unit containing the topic
        unit = None
        for u, topics in syllabus.get("topics", {}).items():
            if topic in topics:
                unit = u
                break
        
        if not unit:
            unit = random.choice(list(syllabus.get("topics", {}).keys()))

        return {
            "board": board,
            "subject": subject,
            "class": class_level,
            "unit": unit,
            "topic": topic,
            "learning_objectives": self._generate_learning_objectives(subject, topic, class_level),
            "prerequisites": self._generate_prerequisites(subject, topic, class_level),
            "materials_needed": self._generate_materials(subject, topic),
            "lesson_structure": self._generate_lesson_structure(subject, topic, class_level),
            "assessment_methods": self._generate_assessment_methods(subject, topic),
            "homework": self._generate_homework(subject, topic, class_level)
        }

    def _generate_learning_objectives(self, subject: str, topic: str, class_level: str) -> List[str]:
        """Generate learning objectives"""
        objectives = [
            f"Understand the concept of {topic}",
            f"Apply {topic} in real-life situations",
            f"Solve problems related to {topic}",
            f"Analyze and interpret {topic} concepts"
        ]
        return objectives

    def _generate_prerequisites(self, subject: str, topic: str, class_level: str) -> List[str]:
        """Generate prerequisites"""
        return [
            f"Basic understanding of {subject}",
            f"Knowledge of fundamental concepts",
            f"Ability to read and write"
        ]

    def _generate_materials(self, subject: str, topic: str) -> List[str]:
        """Generate materials needed"""
        materials = ["Whiteboard", "Markers", "Textbook"]
        
        if subject == "Mathematics":
            materials.extend(["Ruler", "Compass", "Protractor", "Calculator"])
        elif subject == "Science":
            materials.extend(["Charts", "Models", "Laboratory equipment"])
        elif subject == "English":
            materials.extend(["Dictionary", "Story books", "Grammar charts"])
        
        return materials

    def _generate_lesson_structure(self, subject: str, topic: str, class_level: str) -> List[Dict]:
        """Generate lesson structure"""
        return [
            {
                "time": "5 minutes",
                "activity": "Introduction",
                "description": f"Introduce the topic {topic} and its importance"
            },
            {
                "time": "15 minutes",
                "activity": "Explanation",
                "description": f"Explain the concept of {topic} with examples"
            },
            {
                "time": "20 minutes",
                "activity": "Practice",
                "description": f"Students practice problems related to {topic}"
            },
            {
                "time": "10 minutes",
                "activity": "Assessment",
                "description": f"Quick assessment of understanding {topic}"
            }
        ]

    def _generate_assessment_methods(self, subject: str, topic: str) -> List[str]:
        """Generate assessment methods"""
        return [
            "Oral questioning",
            "Written exercises",
            "Group activities",
            "Individual assessment"
        ]

    def _generate_homework(self, subject: str, topic: str, class_level: str) -> Dict[str, str]:
        """Generate homework assignment"""
        return {
            "title": f"Practice {topic}",
            "description": f"Complete exercises on {topic} from textbook",
            "estimated_time": "30 minutes",
            "due_date": "Next class"
        } 