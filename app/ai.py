from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory


class AI:
    def __init__(self, external_memory, tools=None):
        self.tools = tools if tools else []
        self.langchain_memory = ConversationBufferMemory(memory_key="chat_history")
        self.llm = ChatOpenAI(model_name="gpt-4o", temperature=0)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)
        self.agent_with_history = RunnableWithMessageHistory(
            self.agent_executor,
            lambda session_id: self.langchain_memory.chat_memory,
            input_messages_key="input",
            history_messages_key="chat_history",
        )
        self.external_memory = external_memory

    def __call__(self, message):
        self.langchain_memory.chat_memory.clear()

        for user_message, ai_message in zip(self.external_memory.get_user_messages(), self.external_memory.get_ai_messages()):
            self.langchain_memory.chat_memory.add_user_message(user_message)
            self.langchain_memory.chat_memory.add_ai_message(ai_message)

        self.external_memory.add_user_message(message)

        response = self.agent_with_history.invoke(
            {"input": message},
            config={"configurable": {"session_id": "session_id"}},
        )

        self.external_memory.add_ai_message(response["output"])

        print("Response: ", response)
        return response["output"]
