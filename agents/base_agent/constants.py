"""Constants for the base agent."""


class LLM:
    GPT4_TURBO = 'gpt-4-turbo-preview'
    GPT4 = 'gpt-4'
    GPT3_TURBO = 'gpt-3.5-turbo'
    GPT3_TURBO_16K = 'gpt-3.5-turbo-16k'
    GPT3_INSTRUCT = 'gpt-3.5-turbo-instruct'
    CLAUDE_3_SONNET = "anthropic.claude-3-sonnet-20240229-v1:0"
    CLAUDE_3_HAIKU = "anthropic.claude-3-haiku-20240307-v1:0"
    MISTRAL = "mistral.mistral-7b-instruct-v0:2"
    MISTRAL_8X7B = "mistral.mixtral-8x7b-instruct-v0:1"

    OPENAI = [GPT3_INSTRUCT]
    CHAT_OPENAI = [GPT4_TURBO, GPT4, GPT3_TURBO, GPT3_TURBO_16K]
    BEDROCK = [MISTRAL, MISTRAL_8X7B]
    BEDROCK_CHAT = [CLAUDE_3_SONNET, CLAUDE_3_HAIKU]

    LANGFUSE = {
        GPT4_TURBO: 'gpt-4-turbo',
        GPT4: 'gpt-4',
        GPT3_TURBO: 'gpt-3.5-turbo',
        GPT3_TURBO_16K: 'gpt-3.5-turbo-16k',
        GPT3_INSTRUCT: 'gpt-3.5-turbo-instruct',
        CLAUDE_3_SONNET: "claude-3-sonnet-20240229",
        CLAUDE_3_HAIKU: "claude-3-haiku-20240307",
        MISTRAL: "mistral-7b-instruct",
        MISTRAL_8X7B: "mixtral-8x7b-instruct",
    }
