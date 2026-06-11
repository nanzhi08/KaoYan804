import os
import sys
import tempfile
import unittest
import asyncio
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

os.environ.setdefault("DEEPSEEK_API_KEY", "test-key")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import settings
from app.database import Base, get_db
from app.migrations import run_migrations
from app.models.knowledge_point import KnowledgePoint
from app.models.question import Question, QuestionKnowledgePoint
from app.models.practice_record import PracticeRecord
from app.models.knowledge_mastery import KnowledgeMastery
from app.services import question_service
from app.services import ai_service


class AsyncDbTestCase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        db_path = Path(self.temp_dir.name) / "test.db"
        self.engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")
        self.Session = async_sessionmaker(self.engine, expire_on_commit=False)

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await run_migrations(conn)

    async def asyncTearDown(self):
        await self.engine.dispose()
        self.temp_dir.cleanup()

    async def seed_questions(self):
        async with self.Session() as db:
            root = KnowledgePoint(name="C语言", part="C_programming", chapter="")
            chapter = KnowledgePoint(
                name="数组",
                part="C_programming",
                chapter="1.4",
                parent=root,
            )
            ds_root = KnowledgePoint(name="数据结构", part="data_structure", chapter="")
            ds_chapter = KnowledgePoint(
                name="线性表",
                part="data_structure",
                chapter="2.1",
                parent=ds_root,
            )
            db.add_all([root, chapter, ds_root, ds_chapter])
            await db.flush()

            q1 = Question(
                type="single_choice",
                part="C_programming",
                difficulty=2,
                content="数组下标从几开始？",
                options={"A": "0", "B": "1"},
                answer="A",
            )
            q2 = Question(
                type="multi_choice",
                part="data_structure",
                difficulty=3,
                content="线性表可采用哪些存储结构？",
                options={"A": "顺序", "B": "链式", "C": "散列"},
                answer="AB",
            )
            db.add_all([q1, q2])
            await db.flush()
            db.add_all([
                QuestionKnowledgePoint(question_id=q1.id, knowledge_point_id=chapter.id),
                QuestionKnowledgePoint(question_id=q2.id, knowledge_point_id=ds_chapter.id),
            ])
            await db.commit()
            return q1.id, q2.id, chapter.id


class QuestionServiceTests(AsyncDbTestCase):
    async def test_filters_questions_by_part_chapter_and_type(self):
        _, _, chapter_id = await self.seed_questions()
        async with self.Session() as db:
            questions, total = await question_service.get_questions(
                db,
                q_type="single_choice",
                part="C_programming",
                chapter="1.4",
            )
            self.assertEqual(total, 1)
            self.assertEqual(len(questions), 1)
            self.assertEqual(questions[0].knowledge_points[0].knowledge_point_id, chapter_id)

    async def test_submit_practice_scores_answers_and_records_history(self):
        q1_id, q2_id, chapter_id = await self.seed_questions()
        async with self.Session() as db:
            result = await question_service.submit_practice(
                db,
                {
                    "question_id": q1_id,
                    "user_answer": " A ",
                    "time_spent": 12,
                    "practice_mode": "unit_test",
                },
            )
            self.assertTrue(result["is_correct"])
            self.assertEqual(result["score_ratio"], 1.0)
            self.assertEqual(result["knowledge_point_ids"], [chapter_id])

            mastery_result = await db.execute(
                select(KnowledgeMastery).where(KnowledgeMastery.knowledge_point_id == chapter_id)
            )
            mastery = mastery_result.scalar_one()
            self.assertEqual(mastery.total_attempts, 1)
            self.assertEqual(mastery.correct_attempts, 1)
            self.assertGreater(mastery.mastery_level, 0)
            self.assertIsNotNone(mastery.last_reviewed_at)
            self.assertIsNotNone(mastery.next_review_at)

            partial = await question_service.submit_practice(
                db,
                {
                    "question_id": q2_id,
                    "user_answer": "A",
                    "time_spent": 10,
                    "practice_mode": "unit_test",
                },
            )
            self.assertFalse(partial["is_correct"])
            self.assertEqual(partial["score_ratio"], 0.5)

            history, total = await question_service.get_practice_history(db, mode="unit_test")
            self.assertEqual(total, 2)
            self.assertTrue(all(isinstance(item, PracticeRecord) for item in history))

    async def test_create_question_returns_loaded_knowledge_points(self):
        _, _, chapter_id = await self.seed_questions()
        async with self.Session() as db:
            question = await question_service.create_question(
                db,
                {
                    "type": "single_choice",
                    "part": "C_programming",
                    "difficulty": 1,
                    "content": "sizeof(char) 通常为？",
                    "options": {"A": "1", "B": "4"},
                    "answer": "A",
                    "knowledge_point_ids": [chapter_id],
                },
            )
            data = question_service.question_to_dict(question)
            self.assertEqual(data["knowledge_point_ids"], [chapter_id])

    async def test_migration_table_is_created(self):
        async with self.engine.begin() as conn:
            result = await conn.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'"
            )
            self.assertEqual(result.scalar_one_or_none(), "schema_migrations")

    async def test_ai_provider_reports_missing_key(self):
        old_key = ai_service.settings.DEEPSEEK_API_KEY
        ai_service.settings.DEEPSEEK_API_KEY = ""
        try:
            with self.assertRaisesRegex(RuntimeError, "DEEPSEEK_API_KEY"):
                ai_service.get_provider("deepseek")
        finally:
            ai_service.settings.DEEPSEEK_API_KEY = old_key

    async def test_claude_provider_reports_missing_key(self):
        old_key = ai_service.settings.ANTHROPIC_API_KEY
        ai_service.settings.ANTHROPIC_API_KEY = ""
        try:
            with self.assertRaisesRegex(RuntimeError, "ANTHROPIC_API_KEY"):
                ai_service.get_provider("claude")
        finally:
            ai_service.settings.ANTHROPIC_API_KEY = old_key


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "api_test.db"
        self.upload_dir = Path(self.temp_dir.name) / "uploads"
        self.upload_dir.mkdir()
        self.engine = create_async_engine(f"sqlite+aiosqlite:///{self.db_path}")
        self.Session = async_sessionmaker(self.engine, expire_on_commit=False)
        asyncio.run(self._create_schema())

        self.old_upload_dir = settings.UPLOAD_DIR
        settings.UPLOAD_DIR = str(self.upload_dir)

        from app.main import app

        async def override_get_db():
            async with self.Session() as session:
                yield session

        app.dependency_overrides[get_db] = override_get_db
        self.app = app

    async def _create_schema(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await run_migrations(conn)

    def tearDown(self):
        self.app.dependency_overrides.pop(get_db, None)
        settings.UPLOAD_DIR = self.old_upload_dir
        asyncio.run(self.engine.dispose())
        self.temp_dir.cleanup()

    def test_health_exposes_single_user_boundary(self):
        client = TestClient(self.app)
        response = client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["mode"], "single_user")
        self.assertTrue(data["user_label"])

    def test_progress_and_review_include_unscheduled_mastery(self):
        async def seed_progress_data():
            async with self.Session() as db:
                root = KnowledgePoint(name="C语言", part="C_programming", chapter="")
                chapter = KnowledgePoint(
                    name="数组",
                    part="C_programming",
                    chapter="1.4",
                    parent=root,
                    exam_weight="高频",
                )
                db.add_all([root, chapter])
                await db.flush()

                question = Question(
                    type="single_choice",
                    part="C_programming",
                    difficulty=2,
                    content="数组下标从几开始？",
                    options={"A": "0", "B": "1"},
                    answer="A",
                )
                db.add(question)
                await db.flush()
                db.add(QuestionKnowledgePoint(question_id=question.id, knowledge_point_id=chapter.id))
                db.add(PracticeRecord(question_id=question.id, user_answer="A", is_correct=True))
                db.add(
                    KnowledgeMastery(
                        knowledge_point_id=chapter.id,
                        mastery_level=0.2,
                        ease_factor=2.5,
                        interval_days=0,
                        repetitions=0,
                        total_attempts=1,
                        correct_attempts=1,
                        next_review_at=None,
                    )
                )
                await db.commit()

        asyncio.run(seed_progress_data())
        client = TestClient(self.app)

        overview_response = client.get("/api/progress/overview")
        self.assertEqual(overview_response.status_code, 200)
        overview = overview_response.json()["data"]
        self.assertEqual(overview["today_attempts"], 1)
        self.assertEqual(overview["due_review_count"], 1)
        self.assertEqual(overview["weak_knowledge_count"], 1)
        self.assertGreaterEqual(overview["daily_target"], 10)

        due_response = client.get("/api/review/due")
        self.assertEqual(due_response.status_code, 200)
        due_data = due_response.json()["data"]
        self.assertEqual(due_data["due_count"], 1)
        self.assertEqual(due_data["items"][0]["name"], "数组")

        stats_response = client.get("/api/review/stats")
        self.assertEqual(stats_response.status_code, 200)
        stats = stats_response.json()["data"]
        self.assertEqual(stats["due_now"], 1)
        self.assertEqual(stats["due_this_week"], 1)

    def test_upload_text_document_extracts_content(self):
        client = TestClient(self.app)
        response = client.post(
            "/api/documents/upload",
            files={"file": ("note.txt", b"hello 804", "text/plain")},
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["code"], 0)

        doc_id = body["data"]["id"]
        content_response = client.get(f"/api/documents/{doc_id}/content")
        self.assertEqual(content_response.status_code, 200)
        self.assertEqual(content_response.json()["data"]["content"], "hello 804")

    def test_mock_exam_scores_exactly_150_points(self):
        async def seed_exam_questions():
            async with self.Session() as db:
                specs = [
                    ("data_structure", "single_choice", 10),
                    ("data_structure", "calculation", 1),
                    ("data_structure", "analysis", 2),
                    ("data_structure", "programming", 1),
                    ("C_programming", "single_choice", 10),
                    ("C_programming", "fill_blank", 3),
                    ("C_programming", "program_reading", 3),
                    ("C_programming", "programming", 3),
                ]
                for part, q_type, count in specs:
                    for index in range(count):
                        db.add(
                            Question(
                                type=q_type,
                                part=part,
                                difficulty=2,
                                content=f"{part}-{q_type}-{index}",
                                options={"A": "正确"} if q_type == "single_choice" else None,
                                answer="A",
                            )
                        )
                await db.commit()

        asyncio.run(seed_exam_questions())
        client = TestClient(self.app)

        generate_response = client.post("/api/exam/generate")
        self.assertEqual(generate_response.status_code, 200)
        exam = generate_response.json()["data"]
        self.assertEqual(exam["total_score"], 150)
        self.assertEqual(exam["question_count"], 33)
        self.assertEqual(sum(item["score"] for item in exam["questions"]), 150)

        exam_id = exam["exam_id"]
        start_response = client.post(f"/api/exam/{exam_id}/start")
        self.assertEqual(start_response.status_code, 200)

        answers = {str(item["id"]): "A" for item in exam["questions"]}
        submit_response = client.post(f"/api/exam/{exam_id}/submit", json=answers)
        self.assertEqual(submit_response.status_code, 200)
        result = submit_response.json()["data"]
        self.assertEqual(result["score"], 150)
        self.assertEqual(result["accuracy"], 100.0)
        self.assertTrue(all(item["is_correct"] for item in result["answers"]))

    def test_ai_stream_reports_missing_claude_key(self):
        async def seed_kp():
            async with self.Session() as db:
                root = KnowledgePoint(name="C语言", part="C_programming", chapter="")
                chapter = KnowledgePoint(
                    name="数组",
                    part="C_programming",
                    chapter="1.4",
                    parent=root,
                )
                db.add_all([root, chapter])
                await db.flush()
                db.add(KnowledgeMastery(knowledge_point_id=chapter.id))
                await db.commit()
                return chapter.id

        kp_id = asyncio.run(seed_kp())
        client = TestClient(self.app)
        response = client.post("/api/ai/explain", params={"kp_id": kp_id, "provider": "claude"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("ANTHROPIC_API_KEY", response.text)

    def test_ai_chat_stream_reports_missing_deepseek_key(self):
        old_key = ai_service.settings.DEEPSEEK_API_KEY
        ai_service.settings.DEEPSEEK_API_KEY = ""
        try:
            client = TestClient(self.app)
            response = client.post(
                "/api/ai/chat",
                json={"provider": "deepseek", "message": "hello", "messages": []},
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn("DEEPSEEK_API_KEY", response.text)
        finally:
            ai_service.settings.DEEPSEEK_API_KEY = old_key


if __name__ == "__main__":
    unittest.main()
