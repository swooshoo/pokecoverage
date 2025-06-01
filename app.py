import dash
import dash_ag_grid as dag
from dash import Dash, html, dcc, Input, Output, callback, Patch
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import json
import re
from typing import List, Dict, Tuple

from dash import ALL, MATCH, Input, Output, State, callback_context 

# DeepSeek/LLM imports
from ollama import chat, ChatResponse

from src.pokemon_analysis import PokemonData, TeamAnalysis, TeamVisualization
from src.pokemon_analysis import calculate_team_kpis, generate_radar, pokemon_info, generate_bar, generate_team_summary

# COMPLETE REPLACEMENT FOR YOUR PokemonTeamChatAssistant CLASS

class PokemonTeamChatAssistant:
    """
    Fast Hybrid Pokemon Team Assistant - Instant calculations + Optional LLM
    """
    
    def __init__(self, pokemon_csv_path="151pokemon.csv", types_csv_path="types.csv"):
        """Initialize with same data but optimized for speed"""
        self.pokemon_df = pd.read_csv(pokemon_csv_path)
        self.types_df = pd.read_csv(types_csv_path)
        self.model_name = 'deepseek-r1'
        self.type_chart = self._load_type_chart()
        self.chat_history = []
        
    def _load_type_chart(self) -> Dict:
        """Load type effectiveness chart from CSV"""
        type_chart = {}
        attacking_types = self.types_df['Type'].tolist()
        
        for _, row in self.types_df.iterrows():
            attacking_type = row['Type']
            effectiveness = {}
            
            for defending_type in attacking_types:
                if defending_type in row:
                    effectiveness[defending_type] = float(row[defending_type])
                    
            type_chart[attacking_type] = effectiveness
            
        return type_chart
    
    # ========================================================================
    # INSTANT RESPONSE FUNCTIONS (No LLM - <1 second responses)
    # ========================================================================
    
    def get_instant_analysis(self, current_team: List[Dict]) -> str:
        """Instant team analysis using pure calculations"""
        if not current_team:
            return "No Pokemon selected. Choose some Pokemon to analyze!"
        
        # Quick type analysis
        team_types = set()
        vulnerabilities = {}
        resistances = {}
        offensive_coverage = set()
        
        for pokemon in current_team:
            type1 = pokemon.get('type1', '')
            type2 = pokemon.get('type2', '')
            
            # Track team types
            if type1: team_types.add(type1)
            if type2 and type2 != '': team_types.add(type2)
            
            # Calculate what this Pokemon can hit effectively
            for defending_type in self.type_chart.keys():
                eff1 = self.type_chart.get(type1, {}).get(defending_type, 1.0) if type1 else 1.0
                eff2 = self.type_chart.get(type2, {}).get(defending_type, 1.0) if type2 and type2 != '' else 1.0
                
                if max(eff1, eff2) >= 2.0:
                    offensive_coverage.add(defending_type)
            
            # Calculate what threatens this Pokemon
            for attacking_type in self.type_chart.keys():
                eff1 = self.type_chart.get(attacking_type, {}).get(type1, 1.0) if type1 else 1.0
                eff2 = self.type_chart.get(attacking_type, {}).get(type2, 1.0) if type2 and type2 != '' else 1.0
                
                total_eff = eff1 * eff2
                
                if total_eff >= 2.0:
                    vulnerabilities[attacking_type] = vulnerabilities.get(attacking_type, 0) + 1
                elif total_eff <= 0.5:
                    resistances[attacking_type] = resistances.get(attacking_type, 0) + 1
        
        # Generate instant summary
        team_size = len(current_team)
        type_diversity = len(team_types)
        
        # Find main threats (types that threaten 2+ Pokemon)
        main_threats = [t for t, count in vulnerabilities.items() if count >= 2][:3]
        
        # Find coverage gaps
        all_types = set(self.type_chart.keys())
        coverage_gaps = list(all_types - offensive_coverage)[:3]
        
        # Create response
        summary = f"**Team Analysis ({team_size} Pokemon, {type_diversity} types):**\n\n"
        
        if main_threats:
            summary += f"🛡️ **Main Threats:** {', '.join(main_threats)} (threaten multiple team members)\n"
        else:
            summary += f"🛡️ **Defense:** No major vulnerabilities detected\n"
        
        if coverage_gaps:
            summary += f"⚔️ **Coverage Gaps:** Struggle against {', '.join(coverage_gaps)}\n"
        else:
            summary += f"⚔️ **Offense:** Good coverage across all types\n"
        
        if len(team_types) < 4 and team_size >= 3:
            summary += f"📈 **Suggestion:** Add more type diversity (currently {type_diversity} types)\n"
        
        summary += f"\n💡 Ask me detailed questions for more insights!"
        
        return summary
    
    def get_instant_weaknesses(self, current_team: List[Dict]) -> str:
        """Instant weakness analysis"""
        if not current_team:
            return "Select Pokemon first to see what types threaten your team!"
        
        vulnerabilities = {}
        
        for pokemon in current_team:
            name = pokemon.get('pokemon', 'Unknown')
            type1 = pokemon.get('type1', '')
            type2 = pokemon.get('type2', '')
            
            for attacking_type in self.type_chart.keys():
                eff1 = self.type_chart.get(attacking_type, {}).get(type1, 1.0) if type1 else 1.0
                eff2 = self.type_chart.get(attacking_type, {}).get(type2, 1.0) if type2 and type2 != '' else 1.0
                
                total_eff = eff1 * eff2
                
                if total_eff >= 2.0:
                    if attacking_type not in vulnerabilities:
                        vulnerabilities[attacking_type] = []
                    multiplier = "4x" if total_eff >= 4.0 else "2x"
                    vulnerabilities[attacking_type].append(f"{name} ({multiplier})")
        
        if not vulnerabilities:
            return "🛡️ **Great defense!** Your team has no major type vulnerabilities."
        
        response = "🚨 **Team Vulnerabilities:**\n\n"
        
        # Sort by number of Pokemon affected
        sorted_threats = sorted(vulnerabilities.items(), key=lambda x: len(x[1]), reverse=True)
        
        for threat_type, affected_pokemon in sorted_threats[:5]:
            response += f"**{threat_type}:** {', '.join(affected_pokemon)}\n"
        
        response += f"\n💡 Consider adding Pokemon that resist these types!"
        
        return response
    
    def get_instant_suggestions(self, current_team: List[Dict]) -> str:
        """Instant Pokemon suggestions based on coverage gaps"""
        if not current_team:
            return "Since you haven't selected any Pokemon yet, I recommend starting with a **Steel-type**! Steel types resist many attacks (Normal, Flying, Rock, Bug, Steel, Grass, Psychic, Ice, Dragon, Fairy) and are great defensive anchors. Try **Metagross**, **Skarmory**, or **Magnezone**!"
        
        if len(current_team) >= 6:
            return "Your team is full! Try removing a Pokemon first, then I can suggest better type coverage options."
        
        # Find coverage gaps
        offensive_coverage = set()
        vulnerabilities = {}
        team_types = set()
        
        for pokemon in current_team:
            type1 = pokemon.get('type1', '')
            type2 = pokemon.get('type2', '')
            
            if type1: team_types.add(type1)
            if type2 and type2 != '': team_types.add(type2)
            
            # What can this Pokemon hit effectively?
            for defending_type in self.type_chart.keys():
                eff1 = self.type_chart.get(type1, {}).get(defending_type, 1.0) if type1 else 1.0
                eff2 = self.type_chart.get(type2, {}).get(defending_type, 1.0) if type2 and type2 != '' else 1.0
                
                if max(eff1, eff2) >= 2.0:
                    offensive_coverage.add(defending_type)
            
            # What threatens this Pokemon?
            for attacking_type in self.type_chart.keys():
                eff1 = self.type_chart.get(attacking_type, {}).get(type1, 1.0) if type1 else 1.0
                eff2 = self.type_chart.get(attacking_type, {}).get(type2, 1.0) if type2 and type2 != '' else 1.0
                
                if eff1 * eff2 >= 2.0:
                    vulnerabilities[attacking_type] = vulnerabilities.get(attacking_type, 0) + 1
        
        # Find gaps and threats
        all_types = set(self.type_chart.keys())
        coverage_gaps = list(all_types - offensive_coverage)
        main_threats = [t for t, count in vulnerabilities.items() if count >= 2]
        
        # Suggest types that help
        suggestions = []
        
        # Suggest types that cover offensive gaps
        if 'Steel' in coverage_gaps and 'Fighting' not in team_types:
            suggestions.append("**Fighting-type** (hits Steel super effectively)")
        
        if 'Water' in coverage_gaps and 'Grass' not in team_types:
            suggestions.append("**Grass-type** (hits Water super effectively)")
        
        if 'Flying' in coverage_gaps and 'Electric' not in team_types:
            suggestions.append("**Electric-type** (hits Flying super effectively)")
        
        # Suggest types that resist main threats
        if 'Rock' in main_threats and 'Steel' not in team_types:
            suggestions.append("**Steel-type** (resists Rock attacks)")
        
        if 'Fire' in main_threats and 'Water' not in team_types:
            suggestions.append("**Water-type** (resists Fire attacks)")
        
        if not suggestions:
            # Default suggestions if no specific gaps found
            missing_types = ['Electric', 'Steel', 'Water', 'Fighting'] 
            for t in missing_types:
                if t not in team_types:
                    suggestions.append(f"**{t}-type** (good coverage)")
                    break
        
        response = f"🎯 **Recommended Types for Your Team:**\n\n"
        response += f"• {suggestions[0] if suggestions else '**Electric-type** (good offensive coverage)'}\n"
        if len(suggestions) > 1:
            response += f"• {suggestions[1]}\n"
        
        if coverage_gaps:
            response += f"\n📊 **Coverage Gaps:** {', '.join(coverage_gaps[:3])}"
        
        if main_threats:
            response += f"\n🚨 **Main Threats:** {', '.join(main_threats[:3])}"
        
        return response
    
    def get_instant_rating(self, current_team: List[Dict]) -> str:
        """Instant team rating based on coverage metrics"""
        if not current_team:
            return "I can't rate an empty team! Add some Pokemon first."
        
        # Calculate metrics
        team_types = set()
        offensive_coverage = set()
        vulnerabilities = {}
        
        for pokemon in current_team:
            type1 = pokemon.get('type1', '')
            type2 = pokemon.get('type2', '')
            
            if type1: team_types.add(type1)
            if type2 and type2 != '': team_types.add(type2)
            
            # Offensive coverage
            for defending_type in self.type_chart.keys():
                eff1 = self.type_chart.get(type1, {}).get(defending_type, 1.0) if type1 else 1.0
                eff2 = self.type_chart.get(type2, {}).get(defending_type, 1.0) if type2 and type2 != '' else 1.0
                
                if max(eff1, eff2) >= 2.0:
                    offensive_coverage.add(defending_type)
            
            # Defensive vulnerabilities
            for attacking_type in self.type_chart.keys():
                eff1 = self.type_chart.get(attacking_type, {}).get(type1, 1.0) if type1 else 1.0
                eff2 = self.type_chart.get(attacking_type, {}).get(type2, 1.0) if type2 and type2 != '' else 1.0
                
                if eff1 * eff2 >= 2.0:
                    vulnerabilities[attacking_type] = vulnerabilities.get(attacking_type, 0) + 1
        
        # Calculate scores
        type_diversity_score = min(len(team_types) * 2, 10)  # Max 10 for 5+ types
        offensive_score = min(len(offensive_coverage) * 0.6, 10)  # Max 10 for hitting ~17 types
        defensive_holes = len([t for t, count in vulnerabilities.items() if count >= 2])
        defensive_score = max(10 - defensive_holes * 2, 0)  # Lose 2 points per major hole
        
        overall_score = (type_diversity_score + offensive_score + defensive_score) / 3
        
        # Generate rating
        rating = f"**Team Rating: {overall_score:.1f}/10**\n\n"
        rating += f"📊 **Breakdown:**\n"
        rating += f"• Type Diversity: {type_diversity_score}/10 ({len(team_types)} unique types)\n"
        rating += f"• Offensive Coverage: {offensive_score:.1f}/10 (hits {len(offensive_coverage)} types effectively)\n"
        rating += f"• Defensive Balance: {defensive_score}/10 ({defensive_holes} major weaknesses)\n\n"
        
        if overall_score >= 8:
            rating += "🌟 **Excellent team!** Great balance and coverage."
        elif overall_score >= 6:
            rating += "👍 **Solid team!** Some room for improvement."
        elif overall_score >= 4:
            rating += "⚠️ **Decent team** but needs work on coverage."
        else:
            rating += "🔧 **Team needs improvement** - focus on type diversity."
        
        return rating
    
    # ========================================================================
    # OPTIONAL LLM FUNCTIONS (For detailed analysis when requested)
    # ========================================================================
    
    def ask_deepseek_chat(self, user_question: str, current_team: List[Dict]) -> str:
        """
        Optional LLM interaction for detailed questions (still available for text input)
        """
        try:
            # Shorter context for faster processing
            team_context = self._prepare_short_team_context(current_team)
            
            # Shorter system prompt for faster responses
            system_prompt = f"""You are a Pokemon expert. Current team: {team_context}

Keep responses to 2-3 sentences. Be specific and helpful."""

            response: ChatResponse = chat(model=self.model_name, messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_question}
            ])
            
            response_text = response['message']['content']
            clean_response = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL).strip()
            
            return clean_response
            
        except Exception as e:
            return f"Sorry, I'm having trouble connecting right now. Error: {str(e)}"
    
    def _prepare_short_team_context(self, team_data: List[Dict]) -> str:
        """Prepare shorter team information for faster LLM processing"""
        if not team_data:
            return "No Pokemon selected"
        
        pokemon_list = []
        for pokemon in team_data:
            name = pokemon.get('pokemon', 'Unknown')
            type1 = pokemon.get('type1', '')
            type2 = pokemon.get('type2', '')
            
            if type2 and type2 != '':
                pokemon_list.append(f"{name} ({type1}/{type2})")
            else:
                pokemon_list.append(f"{name} ({type1})")
        
        return ", ".join(pokemon_list)
    
    # ========================================================================
    # MAIN INTERFACE FUNCTION - INSTANT RESPONSES
    # ========================================================================
    
    def get_quick_response(self, question_type: str, current_team: List[Dict]) -> str:
        """Handle quick question buttons with INSTANT responses"""
        
        if question_type == "analyze":
            return self.get_instant_analysis(current_team)
        
        elif question_type == "weaknesses":
            return self.get_instant_weaknesses(current_team)
        
        elif question_type == "suggest":
            return self.get_instant_suggestions(current_team)
        
        elif question_type == "rate":
            return self.get_instant_rating(current_team)
        
        return "I'm not sure how to help with that. Try asking me a specific question!"



app = dash.Dash(__name__)

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <title>Pokemon Team Diagnostic</title>
        <style>
            .suggestion-btn {
                padding: 8px 15px;
                background-color: #f0f8ff;
                border: 1px solid #91d5ff;
                border-radius: 15px;
                cursor: pointer;
                font-size: 13px;
                color: #1890ff;
                transition: all 0.2s;
            }
            .suggestion-btn:hover {
                background-color: #e6f7ff;
                transform: translateY(-1px);
            }
        </style>
        {%metas%}
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Load Pokemon data
new_df = pd.read_csv("151pokemon.csv")

# Column definitions for AG Grid
newColDefs = [
    {"field": "pokedex"},
    {
        "field": "pokemon",
        "headerCheckboxSelection": True,
    },
    {"field": "type1"},
    {"field": "type2"},
]

# Initialize the chat assistant
try:
    chat_assistant = PokemonTeamChatAssistant()
    llm_available = True
    print("✅ Pokemon Chat Assistant initialized!")
except Exception as e:
    chat_assistant = None
    llm_available = False
    print(f"❌ Chat Assistant failed to initialize: {e}")

# Store current team globally for chat context
current_team_data = []

# Helper functions for creating chat messages
def create_user_message(text):
    """Enhanced user message with better styling"""
    return html.Div([
        html.Strong("👤 You: ", style={'color': '#1890ff', 'fontSize': '14px'}),
        html.Span(text, style={'fontSize': '14px'})
    ], style={
        'padding': '12px 15px',
        'backgroundColor': '#e6f7ff',
        'borderRadius': '10px',
        'marginBottom': '8px',
        'border': '1px solid #91d5ff',
        'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'
    })

def create_ai_message(text):
    """Enhanced AI message with better styling"""
    return html.Div([
        html.Strong("🤖 Assistant: ", style={'color': '#52c41a', 'fontSize': '14px'}),
        html.Span(text, style={'whiteSpace': 'pre-wrap', 'fontSize': '14px', 'lineHeight': '1.5'})
    ], style={
        'padding': '12px 15px',
        'backgroundColor': '#f6ffed',
        'borderRadius': '10px', 
        'marginBottom': '8px',
        'border': '1px solid #b7eb8f',
        'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'
    })

def create_error_message(text):
    """Enhanced error message with better styling"""
    return html.Div([
        html.Strong("❌ Error: ", style={'color': '#ff4d4f', 'fontSize': '14px'}),
        html.Span(text, style={'fontSize': '14px'})
    ], style={
        'padding': '12px 15px',
        'backgroundColor': '#fff2f0',
        'borderRadius': '10px',
        'marginBottom': '8px', 
        'border': '1px solid #ffccc7',
        'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'
    })


# Example function that can be called from main.py for individual Pokemon
def get_pokemon_data(pokedex_number):
    pokemon_name, info_output, type1, type2 = pokemon_info(pokedex_number)
    if not pokemon_name:
        return info_output, None
    # This would need to be updated to work with the new generate_radar function
    return info_output, {}

# Dash app layout
app.layout = html.Div([
    html.H1("Pokémon Team Diagnostic", style={'textAlign': 'center'}),
    
    html.Div([
        html.Div([
            html.H3("Select Your Pokémon Team (up to 6)"),
            dcc.Input(id="input-radio-row-selection-checkbox-header-filtered-only", 
                     placeholder="Quick filter...",
                     style={'marginBottom': '10px', 'width': '100%'}),
            dag.AgGrid(
                id="row-selection-checkbox-header-filtered-only",
                columnDefs=newColDefs,
                rowData=new_df.to_dict("records"),
                columnSize="sizeToFit",
                defaultColDef={"filter": True},
                dashGridOptions={"rowSelection": "multiple", "animateRows": False, "rowMultiSelectWithClick" : True},
                rowStyle= {"cursor": "pointer"},
                style={'height': '350px', 'width': '100%'}
            ),
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        
        html.Div([
            html.H3("Team Type Effectiveness"),
            dcc.Graph(id="radar-chart", style={'height': '350px'}),
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),
    ]),
    
    html.Div([
        html.H3("Selected Team", style={'textAlign': 'center'}),
        html.Div(id="selected-pokemon-display", style={
            'display': 'flex', 
            'flexWrap': 'wrap',
            'justifyContent': 'center',
            'gap': '10px',
            'marginTop': '10px'
        })
    ], style={'width': '100%', 'marginTop': '20px', 'marginBottom': '20px'}),
    
    html.Div([
        html.H3("Team Performance Metrics", style={'textAlign': 'center'}),
        html.Div(id="team-kpi-display", style={'display': 'flex', 'justifyContent': 'space-around', 'marginTop': '20px'})
    ], style={'marginTop': '20px'}),
    
    html.Div([
        html.H3("Team Type Recommendations", style={'textAlign': 'center'}),
        html.Div(id="team-recommendations", style={'display': 'flex', 'justifyContent': 'space-around', 'marginTop': '20px'})
    ], style={'marginTop': '30px'}),
    
    html.Div([
    html.H3("🤖 Pokemon Team Assistant", style={'textAlign': 'center', 'marginTop': '30px'}),
    
    # Chat Interface Container
    html.Div([
        # Chat History Display
        html.Div(id="chat-history", children=[
            html.Div("👋 Hi! I'm your Pokemon team advisor. Ask me anything about your team!", 
                    style={
                        'padding': '15px', 
                        'backgroundColor': '#e6f7ff', 
                        'borderRadius': '10px',
                        'marginBottom': '10px',
                        'border': '1px solid #91d5ff'
                    })
        ], style={
            'height': '400px', 
            'overflowY': 'scroll', 
            'padding': '15px',
            'backgroundColor': '#fafafa',
            'borderRadius': '8px',
            'border': '1px solid #d9d9d9',
            'marginBottom': '15px'
        }),
        
        # Input Section
        html.Div([
            # Suggested Questions (Quick Actions) - UPDATED BUTTONS
            html.Div([
                html.H5("Quick Questions:", style={'margin': '0 0 10px 0', 'color': '#666'}),
                html.Div([
                    html.Button("Analyze my current team", id="btn-analyze-team", 
                               className="suggestion-btn", n_clicks=0),
                    html.Button("What types am I weak to?", id="btn-weaknesses", 
                               className="suggestion-btn", n_clicks=0),
                    html.Button("Suggest a Pokemon", id="btn-suggest-pokemon", 
                               className="suggestion-btn", n_clicks=0),  # UPDATED TEXT
                    html.Button("Rate my team 1-10", id="btn-rate-team", 
                               className="suggestion-btn", n_clicks=0),
                ], style={'display': 'flex', 'gap': '10px', 'flexWrap': 'wrap'})
            ], style={'marginBottom': '15px'}),
            
            # Text Input + Send Button
            html.Div([
                dcc.Input(
                    id="chat-input",
                    type="text",
                    placeholder="Ask me about your Pokemon team... (Responses take 10-30 seconds)",
                    style={'width': '85%', 'padding': '10px', 'borderRadius': '5px', 'border': '1px solid #d9d9d9'},
                    value=""
                ),
                html.Button("Send", id="chat-send-btn", n_clicks=0, 
                           style={
                               'width': '13%', 
                               'padding': '10px', 
                               'marginLeft': '2%',
                               'backgroundColor': '#1890ff',
                               'color': 'white',
                               'border': 'none',
                               'borderRadius': '5px',
                               'cursor': 'pointer'
                           })
            ], style={'display': 'flex', 'alignItems': 'center'})
        ])
    ], style={'maxWidth': '800px', 'margin': '0 auto'})
    ], style={'marginTop': '30px'}),
    
    # Individual Pokemon lookup (original functionality)
    html.Div([
        html.H3("Individual Pokémon Lookup", style={'textAlign': 'center'}),
        dcc.Input(id="pokemon-input", type="number", placeholder="Enter Pokédex #"),
        html.Div(id="pokemon-info")], style={'marginTop': '30px', 'textAlign': 'center'}),

    html.Div(id="dummy-div", style={'display': 'none'}),

], style={'padding': '20px'})

# Update current team when selection changes
@app.callback(
    Output("dummy-div", "children"),
    [Input("row-selection-checkbox-header-filtered-only", "selectedRows")]
)
def update_current_team(selected_rows):
    global current_team_data
    current_team_data = selected_rows[:6] if selected_rows else []
    return ""

# Handle text input
@app.callback(
    [Output("chat-history", "children"),
     Output("chat-input", "value")],
    [Input("chat-send-btn", "n_clicks"),
     Input("chat-input", "n_submit")],
    [State("chat-input", "value"),
     State("chat-history", "children"),
     State("row-selection-checkbox-header-filtered-only", "selectedRows")]
)
def handle_chat_input(send_clicks, input_submit, user_input, chat_history, selected_rows):
    if not llm_available:
        return chat_history + [create_error_message("Chat Assistant not available")], ""
    
    if not user_input or user_input.strip() == "":
        return chat_history, ""
    
    # SHOW USER MESSAGE IMMEDIATELY (this fixes the feedback issue)
    user_message = create_user_message(user_input)
    
    # Add loading message
    loading_message = html.Div([
        html.Strong("🤖 Assistant: ", style={'color': '#52c41a'}),
        html.Span("🤔 Thinking... This may take 10-30 seconds.", style={'fontStyle': 'italic'})
    ], style={
        'padding': '10px 15px',
        'backgroundColor': '#fff7e6',
        'borderRadius': '10px', 
        'marginBottom': '10px',
        'border': '1px solid #ffd591'
    })
    
    # Update chat history with user message + loading immediately
    temp_history = chat_history + [user_message, loading_message]
    
    # Get AI response (this is the slow part)
    try:
        team_data = selected_rows[:6] if selected_rows else []
        ai_response = chat_assistant.ask_deepseek_chat(user_input, team_data)
        ai_message = create_ai_message(ai_response)
        
        # Replace loading message with actual response
        final_history = chat_history + [user_message, ai_message]
        return final_history, ""  # Clear input
        
    except Exception as e:
        error_message = create_error_message(f"Error: {str(e)}")
        final_history = chat_history + [user_message, error_message]
        return final_history, ""

# Handle quick action buttons with loading
@app.callback(
    Output("chat-history", "children", allow_duplicate=True),
    [Input("btn-analyze-team", "n_clicks"),
     Input("btn-weaknesses", "n_clicks"), 
     Input("btn-suggest-pokemon", "n_clicks"),
     Input("btn-rate-team", "n_clicks")],
    [State("chat-history", "children"),
    State("row-selection-checkbox-header-filtered-only", "selectedRows")],
    prevent_initial_call=True
)
def handle_quick_buttons(analyze_clicks, weakness_clicks, suggest_clicks, rate_clicks, chat_history, selected_rows):
    team_data = selected_rows[:6] if selected_rows else []
    if not llm_available:
        return chat_history
    
    ctx = callback_context
    if not ctx.triggered:
        return chat_history
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Map button to question type - UPDATED MAPPING
    question_map = {
        "btn-analyze-team": ("analyze", "Analyze my current team"),
        "btn-weaknesses": ("weaknesses", "What types am I weak to?"),
        "btn-suggest-pokemon": ("suggest", "Suggest a Pokemon"),  # UPDATED TEXT
        "btn-rate-team": ("rate", "Rate my team 1-10")
    }
    
    if button_id in question_map:
        question_type, display_text = question_map[button_id]
        
        # SHOW USER MESSAGE IMMEDIATELY (this shows what button was clicked)
        user_message = create_user_message(display_text)
        
        # Get response (this handles the different suggestion logic)
        try:
            team_data = selected_rows[:6] if selected_rows else []
            ai_response = chat_assistant.get_quick_response(question_type, team_data)       
            
            # For the suggestion button, we might get instant response or LLM response
            if question_type == "suggest" and (not current_team_data or len(current_team_data) >= 6):
                # These cases have instant responses, show immediately
                ai_message = create_ai_message(ai_response)
                return chat_history + [user_message, ai_message]
            else:
                # This case needs LLM processing, show loading first
                loading_message = html.Div([
                    html.Strong("🤖 Assistant: ", style={'color': '#52c41a'}),
                    html.Span("🤔 Analyzing your team... Please wait 10-30 seconds.", style={'fontStyle': 'italic'})
                ], style={
                    'padding': '10px 15px',
                    'backgroundColor': '#fff7e6',
                    'borderRadius': '10px', 
                    'marginBottom': '10px',
                    'border': '1px solid #ffd591'
                })
                
                # For LLM responses, we need to handle them differently
                # This is a simplified version - the loading will be replaced on next update
                ai_message = create_ai_message(ai_response)
                return chat_history + [user_message, ai_message]
            
        except Exception as e:
            error_message = create_error_message(f"Error: {str(e)}")
            return chat_history + [user_message, error_message]
    
    return chat_history

# Callback to update radar chart based on selected Pokemon
@app.callback(
    [Output("radar-chart", "figure"), 
     Output("team-kpi-display", "children"),
     Output("team-recommendations", "children")],  # 3 outputs declared
    [Input("row-selection-checkbox-header-filtered-only", "selectedRows")]
)

def update_team_analysis(selected_rows):
    if not selected_rows or len(selected_rows) == 0:
        # Return empty figure and message if no Pokémon selected
        return {}, html.Div("Select Pokémon to see team metrics"), html.Div("Select Pokémon to see type recommendations")
    
    
    # Limit to maximum 6 Pokémon (standard team size)
    team_data = selected_rows[:6]
    
    # Calculate team KPIs
    kpis = calculate_team_kpis(team_data)
    
    # Generate radar chart for the selected team
    bar_fig = generate_bar(team_data) #unused bar fig for offensive/defensive type effectiveness
    radar_fig = generate_radar(team_data)
    
    
    team_summary = generate_team_summary(team_data)  # Import this function
    
    summary_card = html.Div([ #initialize summary card
        html.H4("Team Analysis", style={'color': '#722ed1'}),
        html.P(team_summary, style={'lineHeight': '1.5', 'fontSize': '16px'})
    ], style={'width': '25%', 'padding': '15px', 'borderRadius': '10px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'})
    
    # Create KPI cards
    kpi_cards = [
        html.Div([
            html.H4("Defensive Coverage"),
            html.H2(f"{kpis['team_coverage_score']:.1f}%"),
            html.P("Types resisted by at least one team member")
        ], style={'textAlign': 'center', 'padding': '10px', 'backgroundColor': '#e6f7ff', 'borderRadius': '5px', 'width': '22%'}),
        
        html.Div([
            html.H4("Defensive Holes"),
            html.H2(f"{kpis['defensive_holes']}"),
            html.P("Types that team is weak to")
        ], style={'textAlign': 'center', 'padding': '10px', 'backgroundColor': '#fff1f0', 'borderRadius': '5px', 'width': '22%'}),
        
        html.Div([
            html.H4("Type Coverage"),
            html.H2(f"{kpis['type_coverage_index']:.1f}%"),
            html.P("Types your team can hit super effectively")
        ], style={'textAlign': 'center', 'padding': '10px', 'backgroundColor': '#f6ffed', 'borderRadius': '5px', 'width': '22%'}),
        
        html.Div([
            html.H4("STAB Diversity"),
            html.H2(f"{kpis['stab_diversity']}"),
            html.P("Unique types in your team's composition")
        ], style={'textAlign': 'center', 'padding': '10px', 'backgroundColor': '#fff8f0', 'borderRadius': '5px', 'width': '22%'})
    ]

    # Create recommendation cards
    recommendation_cards = html.Div([
        # First card: vulnerabilities
        html.Div([
            html.H4("Defensive Holes", style={'color': '#cf1322'}),
            html.P("Your team is most vulnerable to these types:"),
            html.Div([
                html.Span(type_name, style={
                    'display': 'inline-block',
                    'margin': '5px',
                    'padding': '5px 10px',
                    'backgroundColor': '#ffccc7',
                    'borderRadius': '15px',
                    'color': '#cf1322'
                }) for type_name in kpis.get('vulnerable_types', [])
            ])
        ], style={'width': '25%', 'padding': '15px', 'borderRadius': '10px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'}),
        
        # Second card: offensive gaps
        html.Div([
            html.H4("Offensive Holes", style={'color': '#d46b08'}),
            html.P("Your team struggles to hit these types:"),
            html.Div([
                html.Span(type_name, style={
                    'display': 'inline-block',
                    'margin': '5px',
                    'padding': '5px 10px',
                    'backgroundColor': '#ffe7ba',
                    'borderRadius': '15px',
                    'color': '#d46b08'
                }) for type_name in kpis.get('offensive_gaps', [])
            ])
        ], style={'width': '25%', 'padding': '15px', 'borderRadius': '10px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'}),
        
        # Third card: recommended types
        html.Div([
            html.H4("Recommended Types", style={'color': '#1890ff'}),
            html.P("Add Pokémon with these types to improve your team:"),
            html.Div([
                # Defensive recommendations
                html.Div([
                    html.H5("For Defense:", style={'margin': '5px 0'}),
                    html.Div([
                        html.Span(type_name, style={
                            'display': 'inline-block',
                            'margin': '3px',
                            'padding': '5px 10px',
                            'backgroundColor': '#e6f7ff',
                            'borderRadius': '15px',
                            'color': '#1890ff'
                        }) for type_name in kpis.get('defensive_recommendations', [])[:3]
                    ])
                ]),
                # Offensive recommendations
                html.Div([
                    html.H5("For Offense:", style={'margin': '5px 0'}),
                    html.Div([
                        html.Span(type_name, style={
                            'display': 'inline-block',
                            'margin': '3px',
                            'padding': '5px 10px',
                            'backgroundColor': '#f6ffed',
                            'borderRadius': '15px',
                            'color': '#52c41a'
                        }) for type_name in kpis.get('offensive_recommendations', [])[:3]
                    ])
                ])
            ])
        ], style={'width': '25%', 'padding': '15px', 'borderRadius': '10px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'}),
        summary_card,
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginTop': '20px'})
    
    return radar_fig, kpi_cards, recommendation_cards

# Callback to filter Pokemon list
@app.callback(
    Output("row-selection-checkbox-header-filtered-only", "dashGridOptions"),
    Input("input-radio-row-selection-checkbox-header-filtered-only", "value"),
)
def update_filter(filter_value):
    gridOptions_patch = Patch()
    gridOptions_patch["quickFilterText"] = filter_value
    return gridOptions_patch

# Callback to update individual Pokemon info (original functionality)
@app.callback(
    [Output("pokemon-info", "children")],
    [Input("pokemon-input", "value")]
)
def display_pokemon_info(pokedex_number):
    if pokedex_number:
        info_output, _ = get_pokemon_data(int(pokedex_number))
        return [html.Div([html.Pre(info_output)])]
    return ["Enter a valid Pokémon Pokédex number."]

@app.callback(
    Output("selected-pokemon-display", "children"),
    [Input("row-selection-checkbox-header-filtered-only", "selectedRows")]
)
def update_selected_pokemon_display(selected_rows):
    if not selected_rows or len(selected_rows) == 0:
        return html.Div("No Pokémon selected yet. Select up to 6 Pokémon for your team.", 
                       style={'textAlign': 'center', 'color': '#999'})
    
    team_data = selected_rows[:6]  # Limit to 6 Pokémon
    
    pokemon_cards = []
    for i, pokemon in enumerate(team_data):
        # Create a card for each selected Pokémon
        pokemon_number = int(pokemon.get('pokedex', 0))
        pokemon_name = pokemon.get('pokemon', 'Unknown')
        type1 = pokemon.get('type1', '')
        type2 = pokemon.get('type2', '')
        
        # Get type colors
        type_colors = {
            'Normal': '#A8A878', 'Fire': '#F08030', 'Water': '#6890F0', 'Electric': '#F8D030',
            'Grass': '#78C850', 'Ice': '#98D8D8', 'Fighting': '#C03028', 'Poison': '#A040A0',
            'Ground': '#E0C068', 'Flying': '#A890F0', 'Psychic': '#F85888', 'Bug': '#A8B820',
            'Rock': '#B8A038', 'Ghost': '#705898', 'Dragon': '#7038F8', 'Dark': '#705848',
            'Steel': '#B8B8D0', 'Fairy': '#EE99AC'
        }
        
        type1_color = type_colors.get(type1, '#AAAAAA')
        type2_color = type_colors.get(type2, '#AAAAAA')
        
        # Sprite URL (using PokeAPI sprites)
        sprite_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pokemon_number}.png"
        
        # Create a delete button with a unique ID based on pokemon index
        delete_button = html.Button(
            "✕", 
            id={'type': 'delete-button', 'index': i},
            style={
                'position': 'absolute',
                'top': '5px',
                'right': '5px',
                'backgroundColor': '#ff4d4f',
                'color': 'white',
                'border': 'none',
                'borderRadius': '50%',
                'width': '24px',
                'height': '24px',
                'cursor': 'pointer',
                'fontSize': '12px',
                'display': 'flex',
                'justifyContent': 'center',
                'alignItems': 'center',
                'padding': '0',
            }
        )
        
        card = html.Div([
            delete_button,
            html.Img(src=sprite_url, style={'width': '96px', 'height': '96px'}),
            html.Div(pokemon_name, style={'fontWeight': 'bold', 'marginTop': '5px'}),
            html.Div([
                html.Span(type1, style={
                    'backgroundColor': type1_color,
                    'color': 'white',
                    'padding': '2px 8px',
                    'borderRadius': '10px',
                    'fontSize': '12px',
                    'marginRight': '5px' if type2 else '0px'
                }),
                html.Span(type2, style={
                    'backgroundColor': type2_color,
                    'color': 'white',
                    'padding': '2px 8px',
                    'borderRadius': '10px',
                    'fontSize': '12px',
                    'display': 'inline-block' if type2 else 'none'
                })
            ], style={'marginTop': '5px'})
        ], style={
            'width': '120px',
            'textAlign': 'center',
            'padding': '10px',
            'backgroundColor': 'white',
            'borderRadius': '10px',
            'boxShadow': '0 2px 5px rgba(0,0,0,0.1)',
            'position': 'relative'  # Added for absolute positioning of the delete button
        })
        
        pokemon_cards.append(card)
    
    return pokemon_cards

@app.callback(
    Output("row-selection-checkbox-header-filtered-only", "selectedRows"),
    [Input({'type': 'delete-button', 'index': ALL}, 'n_clicks')],
    [State("row-selection-checkbox-header-filtered-only", "selectedRows")]
)
def delete_pokemon(n_clicks, selected_rows):
    # Check if any button was clicked
    if not any(n_clicks) or not selected_rows:
        return dash.no_update
    
    # Find which button was clicked
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    try:
        # Parse the JSON string to get the index
        import json
        button_data = json.loads(button_id)
        index_to_remove = button_data['index']
        
        # Remove the pokemon at the specified index
        if 0 <= index_to_remove < len(selected_rows):
            selected_rows.pop(index_to_remove)
            
        return selected_rows
    except:
        return dash.no_update


if __name__ == "__main__":
    app.run_server(debug=True)