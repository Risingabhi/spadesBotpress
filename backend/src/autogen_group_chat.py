import autogen
from user_proxy_webagent import UserProxyWebAgent
from groupchatweb import GroupChatManagerWeb
import asyncio

from websocket_proxy import WebSocketProxy

config_list = [
    {
        "model": "gpt-3.5-turbo",
    }
]
llm_config_assistant = {
    "model":"gpt-3.5-turbo",
    "temperature": 0,
    "config_list": config_list,
}
llm_config_proxy = {
    "model":"gpt-3.5-turbo-0613",
    "temperature": 0,
    "config_list": config_list,
}


#############################################################################################
# this is where you put your Autogen logic, here I have a simple 2 agents with a function call
class AutogenChat():
    def __init__(self,  chat_id: str, websocket: WebSocketProxy):
        self.websocket: WebSocketProxy = websocket
        self.chat_id = chat_id
        self.client_sent_queue = asyncio.Queue()
        self.client_receive_queue = asyncio.Queue()

        self.ticket_allocation_agent = autogen.AssistantAgent(
            name="ticket_allocation_agent",
            llm_config=llm_config_assistant,
            max_consecutive_auto_reply=None,
            system_message="""  You are ticket_allocation_agent.
                                   

                                    INSTRUCTIONS:

                                    you will ALWAYS ask the questions given below one by one and wait for user_proxy input .

                                    1. ALWAYS Welcome the user_proxy to spades labour hire website .Ask the user if he a existing or new,  worker or  client . be brief.
                                    
                                    2. if he says existing proceeed with logging him in using his client/worker id, provide him with www.spades.com
                                    3. if he says he is new worker  , send details  to sales_onboarding_agent_worker
                                    4. if he says he is new client  , send details  to sales_onboarding_agent_worker
                                    5. unless you have confirmed above 4 points , you will not pass information to sales_onboarding_agent


                                     """
                                
                                
        )
        self.sales_onboarding_agent_worker = autogen.AssistantAgent(
            name="sales_onboarding_agent_worker",
            llm_config=llm_config_assistant,
            max_consecutive_auto_reply=None,
            system_message="""You are sales_onboarding_agent_worker. You will always respond after ticket_allocation_agent passes information to you and not before that.
                                    

                                    INSTRUCTIONS:

                                     you will ALWAYS ask the questions given below one by one and wait for user_proxy input. You will not skip any question.answer to all questions is mandatory.

                                    1. Run a qualification check by asking the user if he currently resides in austrailia .
                                    2. ask  if he has full time work rights in austrailia.
                                    3. If worker doesnt pass the qualification check , tell the user that he cant sign up with spades and terminate the chat.
                                    4. If worker passes the qualification check but he isnt ready to sign up , present resources to him to sign up at later stage
                                    5. If worker passes the qualification check and is ready to sign up , ask him whether he will like to sign up via chat or a form 
                                
                                    6. Ask for first name.
                                    7. ask for last name.
                                    8. ask for phone number . validate that the phone number should start with 04 and has 10 digits. if condition is satisfied move to next step else ask to give phone number again.
                                    9. ask for email , location and gender . 
                                    10. provide list of skills and ask user to choose from this list [
                                        "Pickpacker/unskilled labourer", "General/skilled labourer", "Landscape labourer",
                                        "Trade assistant", "Joiner", "Carpenter", "Roofer", "Forklift driver",
                                        "Truck driver MY/HR", "Traffice controller", "Steel fixer", "Concretor",
                                        "Form worker", "Exacator operator", "Plaster/renderer", "Brick layer",
                                        "Painter", "Floor layer", "Electrician", "Plumber waterproffer", "Solar panel installer",
                                        "Fitter", "Caulker", "Crane operator", "Dogger/rigger", "Welder/cutter",
                                        "Warehouse", "Allocator", "Expenses", "Other"
                                                                                    ]
                                    11. ask for work experience in years and ask which industry they would like to work in from this list [
                                                                                                                        "Construction",
                                                                                                                        "Warehouse",
                                                                                                                        "Events",
                                                                                                                        "Transport",
                                                                                                                        "other"
                                                                                                                        ]
                                    12. ask for visa type from this list ["Citizen/permanent resident",
                                                                                "Graduate visa",
                                                                                "Working holiday visa",
                                                                                "Student visa",
                                                                                "Covid visa" ,
                                                                                "other"]
                                    13. ask which licenses they have from this list  [
                                                                                            "Id/passport",
                                                                                            "Australian driver license",
                                                                                            "Whitecard",
                                                                                            "Forklift driver(lf/lo ticket)",
                                                                                            "Working at heights",
                                                                                            "Confined space",
                                                                                            "Scissor lift/boom lift/telehandler operator",
                                                                                            "Asbestos removal",
                                                                                            "Blue card(traffic control)",
                                                                                            "Yellow card (plan implementation-traffic control)",
                                                                                            "Excavator/bobcat(lv ticket/voc)",
                                                                                            "Truck driver(hr/hc)",
                                                                                            "Crane/dogman license",
                                                                                            "Hoist operator"
                                                                                        ]
                                    14. ask if they have PPE.
                                    15. ask if they have any disability 
                                    16. if they have disability ask to describe it
                                    17. ask if they have their own transport .
                                    18. ask if they can start immediately . 
                                    19 if yes, ask for any other information that they would like to share . 
                                    20  ask when they can start and ask for any other information that they would like to share.
                                     
                                    21. Confirm to user that all information that provided is being saved to google sheet for official purpose .
                                    22. ask user if has any questions , do function calling for FAQ.
                                    23. share whatsapp link of spades group 


                                            


                                    """ )


        self.sales_onboarding_agent_client = autogen.AssistantAgent(
            name="sales_onboarding_agent_client",
            llm_config=llm_config_assistant,
            max_consecutive_auto_reply=None,
            system_message="""You are sales_onboarding_agent_client. You will always respond after ticket_allocation_agent passes information to you and not before that.
                                    

                                    INSTRUCTIONS:


                                    1. ask name of company
                                    2. ask what type of workers they looking for from this list  [
                                        "General labourers",
                                        "Skilled labourers",
                                        "Unskilled labourers",
                                        "Drivers/offsiders",
                                        "Welders/cutters",
                                        "Operators, tradesman or others",
                                        "Warehouse staff(pick packers or fl drivers)"
                                    ]
                                    3.ask job suburb
                                    4. tell them to describe task involved in work .
                                    5. ask business email of the client,acknowledge the receipt of email.
                                       WORKFLOW 1:
                                       YOU WILL ASK QUESTIONS BELOW ONE BY ONE
                                    1. ask if they want to place work order.
                                    2. if yes , then ask the following questions.
                                    3. ask job address 
                                    4. ask worker type from this list [
                                        "General labourer (construction)",
                                        "Skilled labourer (specific skills)",
                                        "Unskilled labourers (no skills)",
                                        "Warehouse (pick packer)",
                                        "Traffic controller",
                                        "Forklift driver",
                                        "Carpenter",
                                        "Operator (excavator, bobcat, telehandler)",
                                        "Driver (hr truck)",
                                        "Welder/cutter",
                                        "Operators, tradesmen or others",
                                        "Formworker",
                                        "Steelfixer",
                                        "Concreter",
                                        "others"
                                    ]
                                    5. ask how many workers they need for the job
                                    6. ask job start date
                                    7. ask job description.
                                    8. ask job length
                                    9  ask job supervisor name and number
                                    10 ask if any extra info that they need to provide






                                    """)
        


        

        self.allocation_agent = autogen.AssistantAgent(name="allocation_agent",
            llm_config=llm_config_assistant,
            max_consecutive_auto_reply=20,
            system_message = """
                                    You are allocation_agent. you will match workers with client projects with high precision considering factors such as skill level , location and availability 
                                    you will act according to the instructions given below 

                                    INSTRUCTIONS:

                                    
                                
                                

                                    
                                    """
                                    )


        self.book_keeping_agent = autogen.AssistantAgent(name="book_keeping_agent",
            llm_config=llm_config_assistant,
            max_consecutive_auto_reply=20,
            system_message = """
                                    You are book_keeping_agent. you will automate financial transactions , payroll and reporting thereby maintaining accurate and real time financial records. 
                                    you will act according to the instructions given below 

                                    INSTRUCTIONS:

                                    
                                
                                

                                    
                                    """
                                    )




        self.management_agent =autogen.AssistantAgent(name="management_agent",
            llm_config=llm_config_assistant,
            max_consecutive_auto_reply=20,
            system_message = """
                                    You are management_agent. you will oversee and refine operational workflows  ensuring high level coordination and  decision making efficiency. 
                                    you will act according to the instructions given below 

                                    INSTRUCTIONS:

                                

                                    
                                    """)

        self.user_proxy = UserProxyWebAgent( 
            name="user_proxy",
            human_input_mode="ALWAYS", 
            system_message="""reply to agents in manager""",
            max_consecutive_auto_reply=0,
            # is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config=False,
        )



        # add the queues to communicate 
        self.user_proxy.set_queues(self.client_sent_queue, self.client_receive_queue)

        self.groupchat = autogen.GroupChat(agents=[self.user_proxy, self.ticket_allocation_agent, self.sales_onboarding_agent_worker,self.sales_onboarding_agent_client], messages=[], max_round=500)
        self.manager = GroupChatManagerWeb(groupchat=self.groupchat, 
            llm_config=llm_config_assistant,
            human_input_mode="ALWAYS" )   
 

    async def start(self, message):
        await self.user_proxy.a_initiate_chat(
            self.manager,
            clear_history=True,
            message=message
        )


