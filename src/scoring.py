"""
Scoring Engine Module
Calculates final scores and generates feedback
"""


class ScoringEngine:
    """
    Engine for calculating interview scores based on text mining results
    """
    
    def __init__(self):
        self.difficulty_multipliers = {
            'Junior': 0.9,
            'Mid-level': 1.0,
            'Senior': 1.15
        }
    
    def calculate_scores(self, analysis_result, question_weights, difficulty='Mid-level'):
        """
        Calculate final scores from analysis results
        
        Args:
            analysis_result (dict): Results from TextMiningAnalyzer
            question_weights (dict): Weights for different aspects
            difficulty (str): Difficulty level
            
        Returns:
            dict: Calculated scores
        """
        # Extract component scores
        keyword_score = analysis_result['keyword_analysis']['score']
        tfidf_score = analysis_result['tfidf']['score']
        ner_score = analysis_result['ner']['score']
        sentiment_score = analysis_result['sentiment']['score']
        readability_score = analysis_result['readability']['score']
        structural_score = analysis_result['structural']['score']
        coherence_score = analysis_result['coherence']['score']
        
        # Add similarity if available
        similarity_score = analysis_result['similarity'].get('score', 0) if analysis_result.get('similarity') else 0
        
        # Calculate composite scores
        # Technical Accuracy: keyword coverage + NER + similarity
        technical_accuracy = (
            keyword_score * 0.35 +
            ner_score * 0.35 +
            similarity_score * 0.30
        )
        
        # Depth of Knowledge: TF-IDF + structure + ngrams
        ngram_score = analysis_result['ngrams'].get('score', 0)
        depth_of_knowledge = (
            tfidf_score * 0.40 +
            structural_score * 0.40 +
            ngram_score * 0.20
        )
        
        # Communication Clarity: readability + sentiment + coherence
        communication_clarity = (
            readability_score * 0.40 +
            coherence_score * 0.35 +
            sentiment_score * 0.25
        )
        
        # Apply question-specific weights
        weights = question_weights
        overall_score = (
            technical_accuracy * weights['technical'] +
            depth_of_knowledge * weights['depth'] +
            communication_clarity * weights['structure']
        )
        
        # Apply difficulty multiplier
        multiplier = self.difficulty_multipliers.get(difficulty, 1.0)
        overall_score = min(overall_score * multiplier, 5.0)
        
        # Ensure all scores are within bounds
        return {
            'technical_accuracy': round(min(technical_accuracy, 5.0), 2),
            'depth_of_knowledge': round(min(depth_of_knowledge, 5.0), 2),
            'communication_clarity': round(min(communication_clarity, 5.0), 2),
            'overall': round(min(overall_score, 5.0), 2),
            'components': {
                'keyword': keyword_score,
                'tfidf': tfidf_score,
                'ner': ner_score,
                'sentiment': sentiment_score,
                'readability': readability_score,
                'structural': structural_score,
                'coherence': coherence_score,
                'similarity': similarity_score
            }
        }
    
    def generate_detailed_feedback(self, answer, best_answer, analysis_result, scores):
        """
        Generate comprehensive feedback with comparison
        
        Args:
            answer (str): User's answer
            best_answer (str): Reference answer
            analysis_result (dict): Analysis results
            scores (dict): Calculated scores
            
        Returns:
            dict: Detailed feedback with multiple sections
        """
        strengths = []
        improvements = []
        gaps = []
        recommendations = []
        
        # Compare answers
        answer_points = self._extract_key_points(answer)
        best_points = self._extract_key_points(best_answer)
        
        # Identify gaps (apa yang ada di best answer tapi tidak di jawaban user)
        for point in best_points[:5]:  # Ambil 5 point penting dari best answer
            if not any(self._similarity_check(point, ap) for ap in answer_points):
                # Ekstrak kata kunci dari point yang missing
                words = [w for w in point.lower().split() if len(w) > 4][:3]
                if words:
                    gaps.append(f"Tidak menyebutkan tentang {' '.join(words[:2])}")
        
        # Limit gaps
        gaps = gaps[:5]  # Maksimal 5 gaps
        
        # Analyze keyword coverage
        keyword_data = analysis_result['keyword_analysis']
        if keyword_data['coverage'] >= 60:
            strengths.append(
                f"Cakupan keyword sangat baik ({keyword_data['coverage']:.0f}%) - "
                "Anda menyebutkan sebagian besar istilah teknis yang penting"
            )
        elif keyword_data['coverage'] >= 40:
            strengths.append(
                f"Cakupan keyword cukup baik ({keyword_data['coverage']:.0f}%) - "
                "Pemahaman konsep kunci sudah solid"
            )
        elif keyword_data['coverage'] < 30:
            improvements.append(
                f"Cakupan keyword masih kurang ({keyword_data['coverage']:.0f}%) - "
                "Coba sertakan lebih banyak istilah teknis yang relevan"
            )
            recommendations.append(
                "Review kembali konsep kunci untuk topik ini dan pastikan jawaban Anda mencakup semuanya"
            )
        
        # Analyze technical entities
        ner_data = analysis_result['ner']
        if ner_data['total'] >= 5:
            strengths.append(
                f"Kedalaman teknis kuat - menyebutkan {ner_data['total']} tools/methods/metrics spesifik "
                f"dari {ner_data['diversity']} kategori berbeda"
            )
        elif ner_data['total'] >= 3:
            strengths.append(
                f"Referensi teknis bagus - menggunakan {ner_data['total']} istilah spesifik"
            )
        elif ner_data['total'] < 2:
            improvements.append(
                "Kurang spesifik secara teknis - sebutkan nama tools, library, atau metodologi konkret"
            )
            recommendations.append(
                "Sertakan nama spesifik tools/library/framework yang Anda gunakan dalam proyek"
            )
        
        # Analyze structure
        struct_data = analysis_result['structural']
        if struct_data['has_examples'] and struct_data['has_structure']:
            strengths.append(
                "Struktur jawaban rapi dengan contoh konkret - menunjukkan pengalaman praktis"
            )
        elif struct_data['has_examples']:
            strengths.append(
                "Memberikan contoh konkret - demonstrasi pengetahuan praktis yang baik"
            )
        elif not struct_data['has_examples']:
            improvements.append(
                "Tidak ada contoh spesifik - jawaban terasa terlalu teoritis"
            )
            recommendations.append(
                "Gunakan metode STAR: jelaskan Situasi, Tugas, Aksi, dan Result dari pengalaman Anda"
            )
        
        if not struct_data['length_appropriate']:
            if analysis_result['readability']['word_count'] < 50:
                improvements.append(
                    "Jawaban terlalu singkat - berikan penjelasan yang lebih detail"
                )
                recommendations.append(
                    "Target minimal 100 kata. Elaborasi proses berpikir dan reasoning Anda"
                )
            elif analysis_result['readability']['word_count'] > 400:
                improvements.append(
                    "Jawaban cukup panjang - fokus pada poin-poin paling penting"
                )
                recommendations.append(
                    "Latih untuk lebih concise. Target 150-250 kata untuk kebanyakan pertanyaan"
                )
        
        # Analyze readability
        read_data = analysis_result['readability']
        if read_data['assessment'] in ['Excellent', 'Good']:
            strengths.append(
                f"Komunikasi jelas dan terstruktur ({read_data['assessment'].lower()} readability)"
            )
        elif read_data['assessment'] in ['Poor structure', 'Needs improvement']:
            improvements.append(
                f"Readability bisa ditingkatkan - {read_data['assessment'].lower()}"
            )
            recommendations.append(
                f"Panjang kalimat rata-rata Anda {read_data['avg_sentence_length']:.1f} kata. "
                "Target 15-20 kata per kalimat untuk kejelasan optimal"
            )
        
        # Analyze sentiment
        sent_data = analysis_result['sentiment']
        if sent_data['polarity'] > 0.2:
            strengths.append(
                "Tone percaya diri dan positif sepanjang jawaban"
            )
        elif sent_data['polarity'] < -0.1:
            improvements.append(
                "Tone terkesan ragu atau negatif - proyeksikan lebih banyak kepercayaan diri"
            )
            recommendations.append(
                "Gunakan bahasa yang lebih positif. Daripada fokus pada tantangan, tekankan solusi"
            )
        
        # Analyze coherence
        coh_data = analysis_result['coherence']
        if coh_data['score'] >= 4.0:
            strengths.append(
                "Alur logika sangat baik dengan penggunaan kata transisi yang tepat"
            )
        elif coh_data['score'] < 2.5:
            improvements.append(
                "Jawaban kurang koheren - ide-ide terlihat terpisah"
            )
            recommendations.append(
                "Gunakan kata transisi seperti 'namun', 'selain itu', 'oleh karena itu' untuk menghubungkan ide"
            )
        
        # Analyze similarity (if available)
        if 'similarity' in analysis_result and analysis_result['similarity']:
            sim_data = analysis_result['similarity']
            if sim_data['cosine_similarity'] >= 0.5:
                strengths.append(
                    f"Alignment bagus dengan best practices ({sim_data['cosine_similarity']:.0%} kesamaan)"
                )
            elif sim_data['cosine_similarity'] < 0.3:
                improvements.append(
                    "Jawaban cukup berbeda dari pendekatan yang diharapkan"
                )
                recommendations.append(
                    "Pelajari contoh jawaban interview umum untuk topik ini untuk memahami ekspektasi"
                )
        
        # Analyze TF-IDF
        tfidf_data = analysis_result['tfidf']
        if tfidf_data['lexical_diversity'] >= 0.6:
            strengths.append(
                f"Kosakata kaya dengan {tfidf_data['lexical_diversity']:.0%} lexical diversity"
            )
        elif tfidf_data['lexical_diversity'] < 0.3:
            improvements.append(
                "Kosakata terbatas - jawaban terkesan repetitif"
            )
            recommendations.append(
                "Variasikan pilihan kata dan hindari mengulang istilah yang sama"
            )
        
        # Analyze numbers/metrics
        if not struct_data.get('has_numbers', False):
            improvements.append(
                "Tidak ada angka atau metrik - hasil kurang konkret"
            )
            recommendations.append(
                "Kuantifikasi hasil dengan angka spesifik: 'akurasi 87%', 'proses 2 juta records', dll"
            )
        
        # Generate specific actionable feedback
        specific_feedback = self._generate_specific_feedback(
            answer, best_answer, analysis_result, scores
        )
        
        # Generate summary
        summary = self._generate_summary(scores, strengths, improvements)
        
        return {
            'strengths': strengths[:4],
            'improvements': improvements[:4],
            'gaps': gaps if gaps else ["Jawaban Anda sudah cukup lengkap!"],
            'specific_feedback': specific_feedback,
            'summary': summary,
            'recommendations': recommendations[:5]
        }
        
        # Analyze keyword coverage
        keyword_data = analysis_result['keyword_analysis']
        if keyword_data['coverage'] >= 60:
            strengths.append(
                f"Excellent keyword coverage ({keyword_data['coverage']:.0f}%) - "
                "you mentioned most of the expected technical terms"
            )
        elif keyword_data['coverage'] >= 40:
            strengths.append(
                f"Good keyword coverage ({keyword_data['coverage']:.0f}%) - "
                "solid grasp of key concepts"
            )
        elif keyword_data['coverage'] < 30:
            improvements.append(
                f"Low keyword coverage ({keyword_data['coverage']:.0f}%) - "
                "try to incorporate more relevant technical terms"
            )
            recommendations.append(
                "Review the key concepts for this topic and ensure your answer addresses them directly"
            )
        
        # Analyze technical entities
        ner_data = analysis_result['ner']
        if ner_data['total'] >= 5:
            strengths.append(
                f"Strong technical depth - mentioned {ner_data['total']} specific "
                f"tools/methods/metrics across {ner_data['diversity']} categories"
            )
        elif ner_data['total'] >= 3:
            strengths.append(
                f"Good technical references - used {ner_data['total']} specific terms"
            )
        elif ner_data['total'] < 2:
            improvements.append(
                "Limited technical specificity - mention concrete tools, libraries, or methodologies"
            )
            recommendations.append(
                "Include specific names of tools/libraries/frameworks you've used in your projects"
            )
        
        # Analyze structure
        struct_data = analysis_result['structural']
        if struct_data['has_examples'] and struct_data['has_structure']:
            strengths.append(
                "Well-structured answer with concrete examples - demonstrates practical experience"
            )
        elif struct_data['has_examples']:
            strengths.append(
                "Provided concrete examples - good demonstration of practical knowledge"
            )
        elif not struct_data['has_examples']:
            improvements.append(
                "No specific examples provided - answer feels too theoretical"
            )
            recommendations.append(
                "Use the STAR method: describe a Situation, Task, Action, and Result from your experience"
            )
        
        if not struct_data['length_appropriate']:
            if analysis_result['readability']['word_count'] < 50:
                improvements.append(
                    "Answer is too brief - provide more detailed explanation"
                )
                recommendations.append(
                    "Aim for at least 100 words. Elaborate on your thought process and reasoning"
                )
            elif analysis_result['readability']['word_count'] > 400:
                improvements.append(
                    "Answer is quite lengthy - focus on the most important points"
                )
                recommendations.append(
                    "Practice being more concise. Aim for 150-250 words for most questions"
                )
        
        # Analyze readability
        read_data = analysis_result['readability']
        if read_data['assessment'] in ['Excellent', 'Good']:
            strengths.append(
                f"Clear and well-structured writing ({read_data['assessment'].lower()} readability)"
            )
        elif read_data['assessment'] in ['Poor structure', 'Needs improvement']:
            improvements.append(
                f"Readability could be improved - {read_data['assessment'].lower()}"
            )
            recommendations.append(
                f"Your average sentence length is {read_data['avg_sentence_length']:.1f} words. "
                "Aim for 15-20 words per sentence for optimal clarity"
            )
        
        # Analyze sentiment
        sent_data = analysis_result['sentiment']
        if sent_data['polarity'] > 0.2:
            strengths.append(
                "Confident and positive tone throughout your response"
            )
        elif sent_data['polarity'] < -0.1:
            improvements.append(
                "Tone seems uncertain or negative - project more confidence"
            )
            recommendations.append(
                "Use more positive language. Instead of focusing on challenges, emphasize solutions"
            )
        
        # Analyze coherence
        coh_data = analysis_result['coherence']
        if coh_data['score'] >= 4.0:
            strengths.append(
                "Excellent logical flow with good use of transition words"
            )
        elif coh_data['score'] < 2.5:
            improvements.append(
                "Answer lacks coherence - ideas seem disconnected"
            )
            recommendations.append(
                "Use transition words like 'however', 'moreover', 'therefore' to connect your ideas"
            )
        
        # Analyze similarity (if available)
        if 'similarity' in analysis_result and analysis_result['similarity']:
            sim_data = analysis_result['similarity']
            if sim_data['cosine_similarity'] >= 0.5:
                strengths.append(
                    f"Good alignment with best practices ({sim_data['cosine_similarity']:.0%} similarity)"
                )
            elif sim_data['cosine_similarity'] < 0.3:
                improvements.append(
                    "Answer diverges significantly from expected approach"
                )
                recommendations.append(
                    "Research common interview answers for this topic to understand what's typically expected"
                )
        
        # Analyze TF-IDF
        tfidf_data = analysis_result['tfidf']
        if tfidf_data['lexical_diversity'] >= 0.6:
            strengths.append(
                f"Rich vocabulary with {tfidf_data['lexical_diversity']:.0%} lexical diversity"
            )
        elif tfidf_data['lexical_diversity'] < 0.3:
            improvements.append(
                "Limited vocabulary - answer seems repetitive"
            )
            recommendations.append(
                "Vary your word choice and avoid repeating the same terms"
            )
        
        # Overall recommendations based on score
        overall_score = scores['overall']
        if overall_score >= 4.0:
            recommendations.append(
                "Excellent response! Continue practicing with more challenging questions"
            )
        elif overall_score >= 3.0:
            recommendations.append(
                "Solid foundation. Focus on adding more technical depth and specific examples"
            )
        else:
            recommendations.append(
                "Keep practicing! Review fundamental concepts and study sample answers"
            )
        
        # Limit to top items
        # Generate specific actionable feedback
        specific_feedback = self._generate_specific_feedback(
            answer, best_answer, analysis_result, scores
        )
        
        # Generate summary
        summary = self._generate_summary(scores, strengths, improvements)
        
        return {
            'strengths': strengths[:4],
            'improvements': improvements[:4],
            'gaps': gaps,
            'specific_feedback': specific_feedback,
            'summary': summary,
            'recommendations': recommendations[:5]
        }
    
    def _extract_key_points(self, text):
        """Extract key points from text"""
        # Split into sentences
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
        # Return first 10 meaningful sentences
        return sentences[:10]
    
    def _similarity_check(self, text1, text2):
        """Check if two texts are similar"""
        # Simple word overlap check
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        overlap = len(words1.intersection(words2))
        return overlap > 3
    
    def _generate_specific_feedback(self, answer, best_answer, analysis, scores):
        """Generate specific actionable feedback"""
        feedback_parts = []
        
        # Technical accuracy feedback
        if scores['technical_accuracy'] < 3.5:
            feedback_parts.append(
                "**Technical Depth:** Your answer lacks sufficient technical details. "
                "Include specific tools, libraries, and methodologies you've used. "
                "For example, instead of saying 'I analyzed data', say 'I used pandas "
                "to analyze 2M records with 15 features, handling missing values through "
                "KNN imputation.'"
            )
        
        # Keyword feedback
        kw_data = analysis['keyword_analysis']
        if kw_data['coverage'] < 50:
            missing = set(kw_data['expected_keywords']) - set(kw_data['found_keywords'])
            feedback_parts.append(
                f"**Key Concepts Missing:** Your answer doesn't cover important concepts "
                f"like: {', '.join(list(missing)[:5])}. Make sure to address all aspects "
                f"of the question."
            )
        
        # Structure feedback
        struct_data = analysis['structural']
        if not struct_data['has_examples']:
            feedback_parts.append(
                "**Concrete Examples:** Add specific examples from your experience. "
                "Use the STAR method: Situation (context), Task (challenge), "
                "Action (what you did), Result (outcome with metrics)."
            )
        
        # Quantification feedback
        if not struct_data['has_numbers']:
            feedback_parts.append(
                "**Quantify Results:** Include specific metrics and numbers. "
                "For example: 'improved model accuracy by 15%', 'reduced processing time "
                "from 2 hours to 15 minutes', or 'analyzed dataset with 1M+ rows'."
            )
        
        # Communication feedback
        if scores['communication_clarity'] < 3.5:
            feedback_parts.append(
                "**Clarity:** Your answer could be clearer. Break down complex ideas "
                "into simpler terms. Avoid jargon unless necessary, and when you use "
                "technical terms, briefly explain them in business context."
            )
        
        # Best practice comparison
        if analysis.get('similarity', {}).get('cosine_similarity', 0) < 0.4:
            feedback_parts.append(
                "**Alignment with Best Practices:** Your answer differs significantly "
                "from expected responses. Review the example answer to understand what "
                "interviewers typically look for. Focus on: business impact, technical "
                "implementation, problem-solving approach, and measurable outcomes."
            )
        
        return "\n\n".join(feedback_parts) if feedback_parts else \
               "Your answer is well-structured and covers the key points effectively!"
    
    def _generate_summary(self, scores, strengths, improvements):
        """Generate overall summary"""
        overall = scores['overall']
        
        if overall >= 4.5:
            return (
                "**Outstanding Performance!** Your answer demonstrates strong technical "
                "knowledge, clear communication, and practical experience. You're "
                "well-prepared for data science interviews. Continue practicing with "
                "more advanced questions and focus on explaining complex concepts simply."
            )
        elif overall >= 4.0:
            return (
                "**Very Good!** You have a solid foundation and communicate your ideas "
                "well. Minor improvements in technical depth or specific examples would "
                "make your answer even stronger. Focus on quantifying your achievements "
                "and connecting technical work to business value."
            )
        elif overall >= 3.5:
            return (
                "**Good Progress!** Your answer covers the basics well. To improve, add "
                "more specific technical details, concrete examples from your experience, "
                "and quantifiable results. Practice explaining your approach step-by-step "
                "and connecting it to business impact."
            )
        elif overall >= 3.0:
            return (
                "**Fair Performance.** You understand the concepts but need more detail "
                "and structure. Focus on: 1) Adding specific tools/technologies, "
                "2) Providing concrete examples, 3) Quantifying results, 4) Using "
                "the STAR method to structure your answer."
            )
        else:
            return (
                "**Needs Improvement.** Your answer needs significant work. Key areas: "
                "1) Study core concepts more deeply, 2) Practice with real examples, "
                "3) Learn to structure answers using STAR method, 4) Research common "
                "interview questions and model answers. Don't be discouraged - keep "
                "practicing daily!"
            )
    
    def get_percentile_rank(self, score, historical_scores):
        """
        Calculate percentile rank compared to historical scores
        
        Args:
            score (float): Current score
            historical_scores (list): List of previous scores
            
        Returns:
            float: Percentile rank (0-100)
        """
        if not historical_scores:
            return 50.0
        
        below_count = sum(1 for s in historical_scores if s < score)
        percentile = (below_count / len(historical_scores)) * 100
        
        return round(percentile, 1)
    
    def generate_improvement_plan(self, scores, analysis_result):
        """
        Generate personalized improvement plan
        
        Args:
            scores (dict): Score breakdown
            analysis_result (dict): Analysis results
            
        Returns:
            dict: Improvement plan with focus areas
        """
        focus_areas = []
        
        # Identify weakest areas
        component_scores = scores['components']
        sorted_components = sorted(component_scores.items(), key=lambda x: x[1])
        
        weak_components = [comp for comp, score in sorted_components[:3] if score < 3.5]
        
        improvement_map = {
            'keyword': {
                'area': 'Technical Terminology',
                'action': 'Study key terms and concepts related to data science',
                'resources': ['Online glossaries', 'Technical blogs', 'Documentation']
            },
            'ner': {
                'area': 'Tool & Technology Knowledge',
                'action': 'Learn and practice with specific tools and libraries',
                'resources': ['Online courses', 'Hands-on projects', 'GitHub repositories']
            },
            'readability': {
                'area': 'Communication Clarity',
                'action': 'Practice writing clear, concise explanations',
                'resources': ['Writing workshops', 'Technical writing guides', 'Peer review']
            },
            'structural': {
                'area': 'Answer Organization',
                'action': 'Use frameworks like STAR method for structured responses',
                'resources': ['Interview prep books', 'Mock interviews', 'Feedback sessions']
            },
            'coherence': {
                'area': 'Logical Flow',
                'action': 'Practice connecting ideas with transition words',
                'resources': ['Writing exercises', 'Outlining practice', 'Essay analysis']
            },
            'similarity': {
                'area': 'Expected Content Coverage',
                'action': 'Research common interview questions and model answers',
                'resources': ['Interview prep sites', 'YouTube channels', 'Mentor feedback']
            }
        }
        
        for comp in weak_components:
            if comp in improvement_map:
                focus_areas.append(improvement_map[comp])
        
        return {
            'priority_areas': focus_areas,
            'overall_recommendation': self._get_overall_recommendation(scores['overall'])
        }
    
    def _get_overall_recommendation(self, overall_score):
        """Get overall recommendation based on score"""
        if overall_score >= 4.5:
            return "Outstanding! You're interview-ready. Focus on advanced topics and leadership scenarios."
        elif overall_score >= 4.0:
            return "Very good! Polish your answers and practice under time pressure."
        elif overall_score >= 3.5:
            return "Good foundation. Work on technical depth and providing concrete examples."
        elif overall_score >= 3.0:
            return "Decent start. Focus on improving technical accuracy and communication clarity."
        elif overall_score >= 2.5:
            return "Needs improvement. Review fundamental concepts and practice regularly."
        else:
            return "Significant work needed. Start with basics and gradually build up complexity."
