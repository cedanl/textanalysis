#### TO DO ####

# CHANGE THE PATH OF THE TREETAGGER ON LINE 113 TO YOUR OWN DIRECTORY


# Clear workspace
rm(list = ls())
options(warn = 1)  # Make all warnings into errors to catch them with tryCatch

# List of required packages
packages <- c(
  "jsonlite", "readxl", "tidyverse", "cld3", "base64enc", "knitr" ,
  "tidytext", "topicmodels", "tm", "koRpus", "ldatuning",
  "openxlsx", "devtools"
)

# Function to install and load packages
install_and_load <- function(pkg) {
  suppressWarnings(suppressMessages({
    if (!require(pkg, character.only = TRUE)) {
      install.packages(pkg, dependencies = TRUE, repos='http://cran.us.r-project.org')
      devtools::install("unDocUMeantIt/koRpus.lang.en")
      devtools::install("unDocUMeantIt/koRpus.lang.nl")
      library(pkg, character.only = TRUE)
    }
  }))
}

# Apply the function to all packages
invisible(lapply(packages, install_and_load))

# Install packages from GitHub if not available on CRAN
if (!require("koRpus.lang.nl", character.only = TRUE)) {
  suppressWarnings(suppressMessages({
    if (!require("devtools", character.only = TRUE)) {
      install.packages("devtools", dependencies = TRUE)
    }
    devtools::install_github("unDocUMeantIt/koRpus.lang.nl")
    library("koRpus.lang.nl", character.only = TRUE)
  }))
}

if (!require("koRpus.lang.en", character.only = TRUE)) {
  suppressWarnings(suppressMessages({
    if (!require("devtools", character.only = TRUE)) {
      install.packages("devtools", dependencies = TRUE)
    }
    devtools::install_github("unDocUMeantIt/koRpus.lang.en")
    library("koRpus.lang.en", character.only = TRUE)
  }))
}


read_filter_words <- function(filterwords_file) {
  if (file.exists(filterwords_file)) {
    # Read the filter file and split by newline
    filter_words <- readLines(filterwords_file)
    
    # Remove duplicates and empty values
    filter_words <- unique(filter_words[filter_words != ""])
    
    # Return the filter words or empty if none found
    if (length(filter_words) > 0) {
      return(filter_words)
    }
  }
  # Return empty vector if file doesn't exist or is empty
  return(c())
}

# Function to read and preprocess data
read_and_preprocess_data <- function(file_name, sheet_name, column_name, label, question_number, filterwords_file) {

  # Read data from Excel file, specifying the sheet name if provided
  if (!is.null(sheet_name)) {
    data <- read_excel(file_name, sheet = sheet_name)
  } else {
    data <- read_excel(file_name)
  }


  # Convert all data to character type
  data[] <- lapply(data, as.character)

  # Create first column with label
  data[[label]] <- data[[1]]

  # Load question filter from file
  question_filter <- read_filter_words(filterwords_file)

  # Remove rows with missing or short answers
  data <- data[!(is.na(data[[column_name]]) |
                   data[[column_name]] == "" |
                   data[[column_name]] == "-" |
                   nchar(data[[column_name]]) < 5), ]

  # Add question id based on label
  data <- data %>%
    mutate(qid = case_when(
      paste0("q", question_number) == label ~ question_number
    ))

  # Calculate response length per answer
  data <- data %>% mutate(resp_len = str_count(data[[column_name]], "\\w+"))

  # Add answer ids
  data <- data %>% mutate(id = 1:nrow(data))

  return(list(data = data, question_filter = question_filter))
}


# Define the lemmatize function

#### TO DO ####
#### unhardcode path
lemmatize <- function(words) {
  set.kRp.env(TT.cmd="manual", TT.options=list(path="", preset='en', no.unknown=T), lang='en')
  res <- treetag(
    file=words,
    treetagger="kRp.env",
    format="obj",
    stopwords = tm::stopwords('en'))
  
  tokens <- res@tokens
  tokens <- transform(tokens, lemma = ifelse(stop == TRUE, "<stopword>", lemma))
  tokens$lemma <- gsub("\\|.*", "", tokens$lemma)
  
  return(tokens$lemma)
}


# Function to preprocess text and create document-term matrix
preprocess_text <- function(data,column_name,question_number, question_filter) {
  
  # Select data for the chosen question
  data_selection <- subset(data, qid %in% c(question_number))

  # Detect language
  languages <- detect_language(data_selection[[column_name]])
  data_selection <- data_selection[languages == 'nl', ] %>% drop_na()
  

  stop_words <- data.frame(word = tm::stopwords("nl"))
  
  # Create dataframe with individual words
  data_words <- data_selection %>%
    unnest_tokens(word, {{ column_name }}) %>%
    anti_join(stop_words, by = "word")
  
  # Remove numbers and punctuation
  data_words <- data_words %>% filter(!str_detect(word, "[0-9]+|[[:punct:]]|\\(.*\\)"))

  # Apply lemmatization function to words
  data_words$word <- lemmatize(data_words$word)
  
  # Remove stopwords, unknown words, and words from question_filter
  data_words <- data_words %>% filter(!word %in% c("<stopword>", "<unknown>", question_filter))
  
  # Show most common words
  data_words %>% count(word, sort = TRUE) %>% head(30) %>% kable()
  
  # Create document-term matrix
  dfm <- data_words %>%
    count(id, word) %>%
    cast_dfm(id, word, n)
  
  return(list(dfm = dfm, data_selection = data_selection))
}


# Function to determine optimal number of topics
determine_optimal_topics <- function(dfm) {
  # Determine approximate number of topics
  result <- ldatuning::FindTopicsNumber(
    dfm,
    topics = seq(from = 2, to = 10, by = 1),
    metrics = c("CaoJuan2009", "Deveaud2014"),
    method = "Gibbs",
    control = list(seed = 77),
    verbose = TRUE
  )
  plot_path <- tempfile(fileext = ".png")
  png(filename = plot_path)
  FindTopicsNumber_plot(result)
  dev.off()
  
  plot_base64 <- base64encode(plot_path)
  cat("TYPE:IMAGE\n")
  cat(plot_base64)
  cat("\nENDOFIMAGE\n")
  
  unlink(plot_path)
}

# Function to fit the topic model
fit_topic_model <- function(dfm, nr_of_topics) {
  # Fit topic model
  TopicModel <- LDA(dfm, k = nr_of_topics, control = list(seed = 20))
  
  return(TopicModel)
}
# Function to extract top terms per topic
extract_top_terms <- function(TopicModel) {
  # Get word probabilities per topic (beta matrix)
  topics_word <- tidy(TopicModel, matrix = "beta")
  
  # Get top terms per topic
  top_terms <- topics_word %>%
    group_by(topic) %>%
    slice_max(beta, n = 20, with_ties = FALSE) %>%
    ungroup()
  
  # Convert top_terms to JSON and output
  top_terms_json <- toJSON(top_terms)
  cat("TYPE:TOP_TERMS\n")
  cat(top_terms_json)
  cat("\nENDOFTERMS\n")
  
  return(top_terms)
}

# Function to generate document-topic probabilities and merge with data
generate_document_topic_probabilities <- function(TopicModel, dfm, data_selection,column_name, nr_of_topics, top_terms) {
  # Get document-topic probabilities (gamma matrix)
  gamma_matrix <- tidy(TopicModel, matrix = "gamma",
                       document_names = as.integer(rownames(dfm))) %>%
    mutate(topic = factor(topic), document = as.numeric(document))
  
  # Merge gamma values with original data
  joined_df <- gamma_matrix %>% mutate(document = as.numeric(document)) %>%
    left_join(data_selection, by = c('document' = 'id'))
  
  df_topic <- joined_df %>% filter(topic == 1)
  df_full <- df_topic %>% select({{ column_name }}, "resp_len")

  
  # Process results for topics 1 to n
  for (topic_nr in 1:nr_of_topics) {
    selection <- top_terms[top_terms$topic == topic_nr, ]
    str_list <- list(selection$term)
    topic_words <- gsub('^c|\\(|\\)|\\"', "", str_list)
    
    df_topic <- joined_df %>% filter(topic == topic_nr)
    df_full[topic_words] <- df_topic$gamma
  }
  
  return(df_full)
}


#####################################################################################

# Get arguments passed from Python
args <- commandArgs(trailingOnly = TRUE)
working_directory <- args[1]  # Argument 1 is the file path
setwd(working_directory)

file_name <- args[2]
sheet_name <- args[3]
column_name <- args[4]
question_number <- 1
label <- paste0("q", question_number)
nr_of_topics <- as.integer(args[5])

#nr_of_topics <- 3
filterwords_file <- args[6]

#####################################################################################
# file_name <- "output_topic_done_q1.xlsx"
# sheet_name <- "Sheet 1"
# column_name <- "AliHastam11"
# question_number <- 1
# label <- paste0("q", question_number)
# nr_of_topics <- 3
# filterwords_file <- "Topic_Modeling_analysis_AliHastam_2024-12-02.txt"
#####################################################################################


tryCatch({
  
  message("Starting Topic Modeling Analysis")
  #cat("file_path_r:", working_directory, "\n")
  #cat(getwed())
  # cat("file_name:", file_name, "\n")
  # cat("sheet_name:", sheet_name, "\n")
  # cat("column_name:", column_name, "\n")
  # cat("label:", label, "\n")
  # cat("nr_of_topics:", nr_of_topics, "\n")
  # cat("filter_words_file:", filterwords_file, "\n")

  # Step 1: Read and preprocess data
  preprocess_result <- read_and_preprocess_data(file_name, sheet_name, column_name, label, question_number, filterwords_file)
  data <- preprocess_result$data
  question_filter <- preprocess_result$question_filter
  message("Data read and preprocessed")
  
  # Step 2: Preprocess text and create document-term matrix
  text_preprocess_result <- preprocess_text(data, column_name, question_number, question_filter)
  dfm <- text_preprocess_result$dfm
  data_selection <- text_preprocess_result$data_selection

  message("Text preprocessed and document-term matrix created")  


  # Step 3: Determine optimal number of topics
  determine_optimal_topics(dfm)
  
  message("Optimal number of topics determined")
  # Step 4: Fit the topic model
  TopicModel <- fit_topic_model(dfm, nr_of_topics)
  

  message("Topic model fitted")

  # Step 5: Extract top terms per topic and plot
  top_terms <- extract_top_terms(TopicModel)

  message("Top terms extracted")

  # Step 6: Generate document-topic probabilities and merge with data
  df_full <- generate_document_topic_probabilities(TopicModel, dfm, data_selection,column_name, nr_of_topics, top_terms)


  message("Document-topic probabilities generated and merged with data")
  #Specify the output file name
  #output_file <- paste0("output_topic_done_", label, ".xlsx")
  #Write the data frame to an Excel file
  #write.xlsx(df_full, file = output_file)
 }, error = function(e) {
  # Print error message to console
  print(paste("An error occurred: ", e$message))
  #writeLines(c("An error occurred:", e$message))
})

