CREATE TABLE ai_assistant(
    id int NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    product_name VARCHAR(200),
    promt VARCHAR(1024),
    suggestions VARCHAR(500)[],
    greetings VARCHAR(500)[],
    created_time DATE DEFAULT CURRENT_DATE,
    updated_time DATE DEFAULT CURRENT_DATE
)