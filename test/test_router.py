import requests
import logging
import time

logger = logging.getLogger()
logger.addHandler(logging.FileHandler("./test/test_router.log", "w"))
logger.addHandler(logging.StreamHandler())
# logfile = open("./test/test_router.log", "w")

mapping = {
    4:	"Human Anatomy",
    17:	"Linear Inequalities",
    18:	"Permuation and Combination",
    19:	"Laws of Motion",
    20:	"Anatomy of Flowering Plants",
}

data = [
    (3, "What is the structure of the human skeleton?", 4),
    (3, "Explain the functions of the circulatory system.", 4),
    (3, "What are the types of muscles in the human body?", 4),
    (3, "Describe the role of the nervous system in humans.", 4),
    (3, "How does the human skeletal system interact with the muscular system to facilitate movement, and what are some common disorders that can disrupt this interaction?", 4),
    (3, "Discuss the process by which oxygenated blood is transported to the brain and how it differs from the process in other parts of the body.", 4),
    (3, "How do the various types of muscle fibers differ in their structure, function, and adaptability to physical exercise?", 4),
    (3, "In what ways does the autonomic nervous system regulate involuntary actions, and how do disorders of this system affect homeostasis?", 4),
    (3, "What mechanisms enable the body to maintain its posture?", 4),
    (3, "How do the body's internal systems work together during physical activity?", 4),
    (3, "What factors influence the development and health of bones?", 4),
    (3, "How does the body detect and respond to external stimuli?", 4),
    (3, "What are the implications of muscular disorders on physical performance?", 4),
    (3, "Describe how nutrients are transported to various organs via the circulatory system.", 4),
    (3, "How do lifestyle factors impact the health of the nervous system?", 4),

    (3, "How do you solve a linear inequality?", 17),
    (3, "What are the rules for graphing linear inequalities?", 17),
    (3, "Explain the concept of solution sets in linear inequalities.", 17),
    (3, "What is the difference between strict and non-strict inequalities?", 17),
    (3, "How does the representation of a linear inequality on a graph change when the inequality symbol is reversed, and how can this be used to solve optimization problems?", 17),
    (3, "In the context of real-world problems, explain how linear inequalities can model constraints in resource allocation, and provide an example.", 17),
    (3, "What is the impact of scaling the coefficients of a linear inequality by a negative factor, and how does it affect the inequality and its graphical representation?", 17),
    (3, "What is the graphical interpretation of constraints in optimization?", 17),
    (3, "How do boundary lines change with inequalities in two variables?", 17),
    (3, "Explain the relationship between inequality solutions and shaded regions on a graph.", 17),
    (3, "What are the effects of flipping inequality symbols in mathematical problems?", 17),
    (3, "How do inequalities help in representing limits in real-world scenarios?", 17),
    (3, "Discuss the role of inequalities in financial modeling and budgeting.", 17),

    (3, "What is the formula for permutations?", 18),
    (3, "How do combinations differ from permutations?", 18),
    (3, "Give examples of problems solved using combinations.", 18),
    (3, "Explain the concept of factorial in permutation calculations.", 18),
    (3, "Why is the order of selection important in permutations but not in combinations, and how does this distinction apply to solving probability problems in card games?", 18),
    (3, "Provide a detailed explanation of the principle of inclusion-exclusion and its role in solving problems involving overlapping sets in permutations.", 18),
    (3, "How does the formula for circular permutations differ from linear permutations, and in what scenarios is it applied?", 18),
    (3, "How do you determine the number of arrangements of a group of objects?", 18),
    (3, "Why is the arrangement order significant in certain problems?", 18),
    (3, "What methods are used to count subsets of a set?", 18),
    (3, "How does the concept of repetition influence arrangement problems?", 18),
    (3, "Explain the use of advanced counting techniques in overlapping groups.", 18),
    (3, "What adjustments are made in arrangements involving circular patterns?", 18),

    (3, "What is Newton's second law of motion?", 19),
    (3, "How is acceleration related to force?", 19),
    (3, "What are the applications of the laws of motion in real life?", 19),
    (3, "Explain the concept of inertia.", 19),
    (3, "How does Newton's second law of motion apply to systems involving variable mass, such as rockets, and what are the mathematical modifications required for such scenarios?", 19),
    (3, "Discuss the role of friction in altering the outcomes predicted by Newton's laws of motion, and explain how frictional forces can sometimes be advantageous.", 19),
    (3, "Provide an example of a real-world scenario where Newton's laws of motion fail to accurately describe the behavior of objects, and explain why this happens.", 19),
    (3, "What determines the acceleration of an object in motion?", 19),
    (3, "How are external forces balanced to maintain an object's state of rest?", 19),
    (3, "Describe the effects of unbalanced forces on the motion of objects.", 19),
    (3, "How do varying mass systems challenge basic motion laws?", 19),
    (3, "What happens when theoretical motion laws are applied in high-speed scenarios?", 19),
    (3, "How do surface interactions modify the outcomes predicted by basic physics?", 19),

    (3, "What are the parts of a flowering plant?", 20),
    (3, "Explain the structure of a flower.", 20),
    (3, "What are the functions of xylem and phloem?", 20),
    (3, "Describe the anatomy of a dicot stem.", 20),
    (3, "How do environmental factors such as soil composition and water availability influence the development and anatomy of the xylem and phloem in flowering plants?", 20),
    (3, "Explain the process of pollination in detail, including the roles of different flower parts and how this process varies among plant species.", 20),
    (3, "What are the anatomical and functional differences between monocot and dicot roots, and how do these differences affect their adaptability to different environments?", 20),
    (3, "How do vascular tissues support the growth and transport within plants?", 20),
    (3, "What adaptations enable certain plant structures to survive in dry conditions?", 20),
    (3, "How is food produced in plants distributed to non-photosynthetic parts?", 20),
    (3, "What structural variations exist in the stems of different plant species?", 20),
    (3, "Discuss the role of reproductive structures in plant species diversity.", 20),
    (3, "How do underground root systems contribute to plant stability and nutrition?", 20),
]

# data = [
#     (3, "How does the interaction between specialized tissues enable the dynamic stabilization of internal conditions during external perturbations, and what are the key disruptions that compromise this mechanism?", 4),
#     (3, "When constraints are modeled as non-strict relations among multi-dimensional variables, how does the feasible region's geometric representation shift when transitioning between bounded and unbounded systems?", 17),
#     (3, "In scenarios involving indistinguishable outcomes constrained by overlapping criteria, how do you determine the exact enumeration of unique configurations while avoiding redundant arrangements?", 18),
#     (3, "In the context of a non-inertial reference frame with complex external forces, how does the apparent motion of objects reconcile with classical principles when the reference frame itself is undergoing rotational acceleration?", 19),
#     (3, "How do variations in environmental gradients influence the differential allocation of resources among vascular tissues, and what structural adaptations are observed in extreme cases?", 20)
# ]

# Backend URL
backend_url = "http://localhost:5000/router"
session = requests.Session()

# Function to send POST requests
def send_post_request(query, course_id):
    payload = {
        "course_id": course_id,
        "query": query
    }
    try:
        return session.post(backend_url, json=payload).json()
        
    except requests.exceptions.RequestException as e:
        print(f"Error sending request: {e}")
        # return send_post_request(query, course_id)

correct_count = 0
total_score = 0

starttime0 = time.time()
for course_id, query, expected_response in data:

    result = send_post_request(query, course_id)

    topic_ids = [doc["metadata"]["topic_id"] for doc in result]
    if expected_response in topic_ids:
        correct_count += 1
        score = topic_ids[::-1].index(expected_response) + 1
        total_score += score
        print(f"Sent: {query}, Received: {topic_ids}, Expected: {expected_response}, Score: {score}")
    else:
        print(f"Sent: {query}, Received: {topic_ids}, Expected: {expected_response}, Score: 0")
    # logfile.flush()
endtime0 = time.time()

print(f"Correct responses: {correct_count}/{len(data)} ({correct_count / len(data) * 100}%)")
print(f"Final Score: {total_score}/{len(data) * 3}")
print(f"Average time per query: {(endtime0 - starttime0) / len(data)}")
# logfile.flush()

# logfile.close()
